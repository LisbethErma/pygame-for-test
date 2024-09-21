import pygame
import sqlite3
import random

# Инициализация pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Шрифт
font = pygame.font.Font(None, 36)

# ФПС
clock = pygame.time.Clock()
FPS = 60

# Подключение к базе данных SQLite
conn = sqlite3.connect("game_scores.db")
cursor = conn.cursor()

# Создание таблицы для хранения очков, если её еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                  (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)''')
conn.commit()

# Класс игрока
class Player:
    def __init__(self, name):
        self.name = name
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.width = 50
        self.height = 50
        self.color = GREEN
        self.speed = 5
        self.score = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x - self.speed > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.width + self.speed < WIDTH:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y - self.speed > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y + self.height + self.speed < HEIGHT:
            self.y += self.speed

# Класс для препятствий
class Obstacle:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 50)
        self.y = 0
        self.width = 50
        self.height = 50
        self.color = RED
        self.speed = 5

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0 - self.height
            self.x = random.randint(0, WIDTH - self.width)

# Функция для записи очков в базу данных
def save_score(name, score):
    cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()

# Функция для отображения топ-5 игроков
def show_top_scores():
    cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 5")
    top_scores = cursor.fetchall()
    return top_scores

# Функция для завершения игры
def game_over(player):
    save_score(player.name, player.score)
    top_scores = show_top_scores()
    
    screen.fill(BLACK)
    game_over_text = font.render(f"Game Over! Your score: {player.score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    
    top_text = font.render("Top 5 Players:", True, WHITE)
    screen.blit(top_text, (WIDTH // 2 - top_text.get_width() // 2, HEIGHT // 2 + 10))

    for i, (name, score) in enumerate(top_scores):
        score_text = font.render(f"{i + 1}. {name}: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50 + i * 30))

    pygame.display.update()
    pygame.time.wait(5000)

# Функция для запроса имени игрока через графический интерфейс
def get_player_name():
    name = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10:  # Ограничим длину имени
                    name += event.unicode

        screen.fill(BLACK)
        prompt_text = font.render("Enter your name:", True, WHITE)
        name_text = font.render(name, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))

        pygame.display.update()
        clock.tick(FPS)
    
    return name

# Основная игровая функция
def game_loop():
    player_name = get_player_name()  # Получаем имя игрока через графическое окно
    player = Player(player_name)
    obstacles = [Obstacle() for _ in range(5)]
    
    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys)
        player.draw(screen)
        
        for obstacle in obstacles:
            obstacle.move()
            obstacle.draw(screen)
            
            # Проверка на столкновение
            if (player.x < obstacle.x + obstacle.width and
                player.x + player.width > obstacle.x and
                player.y < obstacle.y + obstacle.height and
                player.y + player.height > obstacle.y):
                running = False
        
        # Подсчет очков
        player.score += 1
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(FPS)
    
    game_over(player)

# Запуск игры
game_loop()

# Закрытие соединения с базой данных
conn.close()
pygame.quit()
