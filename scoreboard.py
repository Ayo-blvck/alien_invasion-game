import pygame.font

class Scoreboard:
    """A class to report score information"""
    
    def __init__(self, ai_game):
        """Initialize scoring attributes"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        
        # Font properties of scoring info
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)
        
        # Prepare initial score image
        self.prep_score()
        
    
    def prep_score(self):
        """Turns score to a rendered image"""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_color, self.settings.bg_color)
        
        # Display at top right of the screen
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 10
        
        
    def show_score(self):
        # Draw score to screen.
        self.screen.blit(self.score_image, self.score_rect)
        
