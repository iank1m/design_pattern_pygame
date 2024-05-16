import pygame
from random import randrange
import time

# 파이게임 화면에 텍스트를 표시하는데 사용할 파란색 색상 정의
BLUE = (0, 0, 255)


class ButtonImplementation:
    def __init__(self, rect, text, font, color):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class NumberButtonImplementation(ButtonImplementation):
    pass

class Button:
    def __init__(self, rect, text, font, color):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.implementation = None

    def set_implementation(self, implementation):
        self.implementation = implementation

    def set_rect(self, rect):
        self.rect = rect

    def draw(self, screen):
        if self.implementation:
            self.implementation.draw(screen)

class NumberButton(Button):
    def set_rect(self, rect):
        self.rect = rect



# ----------------------------------------------
# 적용 패턴: Proxy Pattern
# ButtonProxy 클래스는 Button 클래스의 대리자 역할을 함. 
# 이를 통해 기존의 Button 객체를 대체하여 클라이언트가 해당 객체에 접근할 때 추가적인 작업을 수행할 수 있음
# ----------------------------------------------
class ButtonProxy(Button):
    def __init__(self, button):
        self.button = button
        self.rect = button.rect  # ButtonProxy에도 rect 속성을 추가

    def set_implementation(self, implementation):
        self.button.set_implementation(implementation)

    def set_rect(self, rect):
        self.button.set_rect(rect)

    def draw(self, screen):
        self.button.draw(screen)

    def handle_click(self):
        # 클릭에 대한 추가 작업을 수행할 수 있음
        self.button.handle_click()



# ----------------------------------------------
# 적용 패턴: Factory Pattern
# ButtonFactory 클래스는 Button 객체 및 NumberButton 객체를 생성하는 팩토리를 구현
# ----------------------------------------------

class ButtonFactory:
    @staticmethod
    def create_button(rect, text, font, color):
        button = Button(rect, text, font, color)
        implementation = ButtonImplementation(rect, text, font, color)
        button.set_implementation(implementation)
        return button

    @staticmethod
    def create_number_button(rect, text, font, color):
        button = NumberButton(rect, text, font, color)
        implementation = NumberButtonImplementation(rect, text, font, color)
        button.set_implementation(implementation)
        return button

# ----------------------------------------------
# 적용 패턴 :Facade Pattern
# GameFacade 클래스는 게임을 쉽게 제어할 수 있는 단순한 인터페이스를 제공
# ----------------------------------------------

class GameFacade:
    def __init__(self):
        self.setup_game()
        self.start_background = pygame.image.load("start_background_찐최종본.png")  

    def setup_game(self):
        pygame.init()
        self.screen_width, self.screen_height = 1200, 780
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Memory Game")
        self.game_font = pygame.font.Font(None, 120)

        self.background = pygame.image.load("game_background.png")
        self.sub_screen_width, self.sub_screen_height = 865, 520
        self.sub_screen = pygame.Surface((self.sub_screen_width, self.sub_screen_height))

        self.number_buttons = []
        self.curr_level = 1
        self.display_time = None
        self.start_ticks = None
        self.start = False
        self.hidden = False
        self.score = 0

        self.setup(self.curr_level)

    def setup(self, level):
        self.display_time = max(5 - (level // 3), 1)
        number_count = min((level // 3) + 5, 20)
        self.shuffle_grid(number_count)

    def shuffle_grid(self, number_count):
        rows, columns = 5, 8
        cell_size, button_size = 95, 90
        screen_left_margin, screen_top_margin = 60, 40

        grid = [[0 for col in range(columns)] for row in range(rows)]

        number = 1
        while number <= number_count:
            row_idx = randrange(0, rows)
            col_idx = randrange(0, columns)

            if grid[row_idx][col_idx] == 0:
                grid[row_idx][col_idx] = number
                number += 1

                center_x = screen_left_margin + (col_idx * cell_size) + (cell_size / 2)
                center_y = screen_top_margin + (row_idx * cell_size) + (cell_size / 2)

                rect = pygame.Rect(0, 0, button_size, button_size)
                rect.center = (center_x, center_y)

                button = ButtonFactory.create_number_button(rect, str(number), self.game_font, (255, 255, 255))
                button = ButtonProxy(button)  # 프록시 패턴 적용
                self.number_buttons.append(button)

    def display_start_screen(self):
        start_button_rect = pygame.Rect((self.screen_width/2, self.screen_height/2), (100, 100))  # Example start button rect
        pygame.draw.circle(self.screen, (255, 255, 255), start_button_rect.center, 60, 5)
        msg = self.game_font.render(f"{self.curr_level}", True, (255, 255, 255))
        msg_rect = msg.get_rect(center=start_button_rect.center)
        self.screen.blit(msg, msg_rect)

    def display_game_screen(self):
        if not self.hidden:
            elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
            if elapsed_time > self.display_time:
                self.hidden = True

        for idx, button in enumerate(self.number_buttons, start=1):
            if self.hidden:
                pygame.draw.rect(self.screen, (255, 255, 255), button.rect)
            else:
                cell_text = self.game_font.render(str(idx), True, (255, 255, 255))
                text_rect = cell_text.get_rect(center=button.rect.center)
                self.screen.blit(cell_text, text_rect)

    def increase_score(self, level):
        if level < 4:
            self.score += 10
        else:
            self.score += level + 10

    def draw_score(self):
        font = pygame.font.SysFont("FixedSsy", 70, True, False)
        text_score = font.render("Score: " + str(self.score), True, BLUE)
        text_score_rect = text_score.get_rect(center=(self.screen_width/2 - 160, self.screen_height/2 - 30))
        self.screen.blit(text_score, text_score_rect)
        text_level = font.render(f"Level: {self.curr_level}", True, BLUE)
        text_level_rect = text_level.get_rect(center=(self.screen_width/2 - 160, self.screen_height/2 - 80))
        self.screen.blit(text_level, text_level_rect)

    def check_buttons(self, pos):
        if self.start:
            self.check_number_buttons(pos)
        elif self.start_background.get_rect().collidepoint(pos):  
            self.start = True
            self.start_ticks = pygame.time.get_ticks()

    def check_number_buttons(self, pos):
        for button in self.number_buttons:
            if button.rect.collidepoint(pos):
                if button == self.number_buttons[0]:
                    print("Correct")
                    self.increase_score(self.curr_level)
                    del self.number_buttons[0]
                    if not self.hidden:
                        self.hidden = True
                else:
                    self.game_over()
                break

        if len(self.number_buttons) == 0:
            self.start = False
            self.hidden = False
            self.curr_level += 1
            self.setup(self.curr_level)

    def game_over(self):
        self.draw_score()
        pygame.display.update()
        time.sleep(5)
        pygame.quit()  # 게임 종료 후 Pygame을 종료
        quit()  # Python 인터프리터를 종료

    def run(self):
        fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        fade_surface.fill((0, 0, 0))

        self.screen.blit(self.start_background, (0, 0))  
        pygame.display.update()
        pygame.time.wait(2000)

        fade_alpha = 0
        fade_speed = 5

        while fade_alpha < 255:
            fade_alpha += fade_speed
            fade_surface.set_alpha(fade_alpha)
            self.screen.blit(self.start_background, (0, 0))  
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()

        while fade_alpha > 0:
            fade_alpha -= fade_speed
            fade_surface.set_alpha(fade_alpha)
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()

        running = True
        while running:
            click_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    click_pos = pygame.mouse.get_pos()
                    print(click_pos)
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.sub_screen, (25, 40))

            if self.start:
                self.display_game_screen()
            else:
                self.display_start_screen()

            if click_pos:
                self.check_buttons(click_pos)

            pygame.display.update()

        self.game_over()  # 게임이 종료되면 game_over 메서드를 호출하여 게임 종료 처리


# excute
game = GameFacade()
game.run()
