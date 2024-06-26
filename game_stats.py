class GameStats:
    """Track statistics for Alien Invasions"""
    
    def __init__(self, ai_game):
        """Initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        
    def reset_stats(self):
        """Initialize statistics that can change during game play"""
        self.ships_left = self.settings.ship_limit
        self.score = 0