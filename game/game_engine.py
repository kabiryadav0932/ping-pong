import pygame
from .paddle import Paddle
from .ball import Ball
import random

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        # Initialize paddles and ball
        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        # Scores
        self.player_score = 0
        self.ai_score = 0
        self.winning_score = 5  # default
        self.font = pygame.font.SysFont("Arial", 30)

        # Initialize sounds
        pygame.mixer.init()
        self.paddle_sound = pygame.mixer.Sound("game/sounds/paddle_hit.wav")
        self.wall_sound = pygame.mixer.Sound("game/sounds/wall_bounce.wav")
        self.score_sound = pygame.mixer.Sound("game/sounds/score.wav")

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self, screen):
        # Move the ball
        self.ball.move()

        # --- Ball collision with paddles ---
        if self.ball.rect().colliderect(self.player.rect()) or self.ball.rect().colliderect(self.ai.rect()):
            self.ball.velocity_x *= -1
            self.paddle_sound.play()

        # --- Ball collision with walls ---
        if self.ball.y <= 0 or self.ball.y + self.ball.height >= self.height:
            self.ball.velocity_y *= -1
            self.wall_sound.play()

        # --- Scoring ---
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
            self.score_sound.play()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.ball.reset()
            self.score_sound.play()

        # --- Check for Game Over ---
        if self.player_score >= self.winning_score:
            self.display_winner(screen, "Player Wins!")
            pygame.time.wait(1000)
            self.show_replay_menu(screen)
        elif self.ai_score >= self.winning_score:
            self.display_winner(screen, "AI Wins!")
            pygame.time.wait(1000)
            self.show_replay_menu(screen)

        # AI paddle movement
        self.ai.auto_track(self.ball, self.height)

    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

    # --- Helper methods ---
    def display_winner(self, screen, text):
        screen.fill((0, 0, 0))
        winner_surf = self.font.render(text, True, WHITE)
        screen.blit(winner_surf, (self.width//2 - winner_surf.get_width()//2,
                                  self.height//2 - winner_surf.get_height()//2))
        pygame.display.flip()

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()

    def show_replay_menu(self, screen):
        selecting = True
        while selecting:
            screen.fill((0, 0, 0))
            title = self.font.render("Replay? Press 3 / 5 / 7 for Best of, ESC to Exit", True, WHITE)
            screen.blit(title, (self.width//2 - title.get_width()//2, self.height//2 - 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_3:
                        self.winning_score = 3
                        selecting = False
                    elif event.key == pygame.K_5:
                        self.winning_score = 5
                        selecting = False
                    elif event.key == pygame.K_7:
                        self.winning_score = 7
                        selecting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

        self.reset_game()
