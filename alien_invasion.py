import sys
from time import sleep

import pygame
from pygame.sprite import Sprite

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button

class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        
        # mini window (1200 x 800)
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        # Fullscreen mode
        # self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        
        # Create an instance to store game statistics
        self.stats = GameStats(self)
        
        pygame.display.set_caption("Alien Invasion")
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
        
        # Make Play button
        self.play_button = Button(self, "Play")


    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            
            
    # Watch for keyboard and mouse events.
    def _check_events(self):
        """Responds to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
                    
                    
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos=mouse_pos)


    def _check_keydown_events(self, event):
        """Responds to key presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            if not self.stats.game_active:
                self._check_play_button(event=event)
            else:
                self._fire_bullet()


    def _check_keyup_events(self, event):
        """Responds to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _fire_bullet(self):
        """Create a new bullet and add it to the bullet group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        #Remove bullets that have disappeared (aviod consuming memory)
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions() 
                
                
    def _check_bullet_alien_collisions(self):
            # Check for any bullet that have hit aliens.
            #If so, get rid of the bulet and alien
            collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
            if not self.aliens:
                #Destroy existing bullets and create new fleet.
                self.bullets.empty()
                self._create_fleet()
                # dynamic settings
                self.settings.increase_speed()


    def _create_fleet(self):
        """Create the fleet of aliens"""
        #Make an alien and find number of aliens in a row
        #Spacing between each alien is equal to one alien width
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Alien to Screen Calculation Test 2
        # alien_width, alien_height = int(alien.rect.size // 1.8)
        # available_space_x = self.settings.screen_width - (alien_width + (alien_width / 2))
        # number_aliens_x = int(available_space_x // (alien_width + (alien_width / 2)))
        
        # Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the first row of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)


    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in a row"""
        #Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)


    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the position of all the aliens in the fleet
        """
        self._check_fleet_edges()
        self.aliens.update()
        #Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
        


    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    
    def _ship_hit(self):
        """Responds to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            # Decrement ships left
            self.stats.ships_left -= 1
            
            # remove remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            
            # Create new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()
            self._blink_ship()
            
            # Pause 
            sleep(0.8)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
        
        
    def _blink_ship(self):
        """Blink the ship to indicate a hit."""
        blink_count = 5
        blink_duration = 0.2  # Time in seconds for each blink phase (on/off)
        for _ in range(blink_count):
            self.ship.visible = not self.ship.visible
            self._update_screen()
            sleep(blink_duration)
        self.ship.visible = True  # Ensure ship is visible at the end
        
        
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this as ship got hit
                self._ship_hit()
                break
    
    
    def _check_play_button(self, mouse_pos=None, event=None):
        """Start game when player clicks Play"""
        button_clicked = (mouse_pos and self.play_button.rect.collidepoint(mouse_pos)) or (event and event.key == pygame.K_SPACE)
        if button_clicked and not self.stats.game_active:
            # Reset Game Settings
            self.settings.initialize_dynamic_settings()
            # Reset the statistics
            self.stats.reset_stats()
            self.stats.game_active = True
            # Remove any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            # Hide mouse cursor
            pygame.mouse.set_visible(False)
    
    #Redraw the screen during each pass through the loop
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        if self.ship.visible:
            self.ship.blitme()
        
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()
        
        # Make the most recently drawn screen visible.
        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()