import pygame
import sys
import os

# 初始化 pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Button:
    """按钮类"""
    def __init__(self, text, x, y, width, height, color=GRAY, hover_color=WHITE, text_color=BLACK, font=None):
        """
        初始化按钮
        
        :param text: 按钮文本
        :param x: x坐标
        :param y: y坐标
        :param width: 宽度
        :param height: 高度
        :param color: 默认颜色
        :param hover_color: 悬停颜色
        :param text_color: 文本颜色
        :param font: 字体对象
        """
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover = False
        self.font = font or pygame.font.Font(None, 36)

    def draw(self, screen):
        """绘制按钮"""
        current_color = self.hover_color if self.hover else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # 边框
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hover and event.button == 1:
            return True
        return False

class StartMenu:
    """开始菜单类"""
    def __init__(self, screen_width=800, screen_height=600, title="Gomoku Game"):
        """
        初始化开始菜单
        
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :param title: 窗口标题
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.screen = None
        self.font = None
        self.title_font = None
        self.buttons = []
        self.running = True
        self.choice = None
        
        self._init_display()
        self._init_fonts()
        self._create_buttons()

    def _init_display(self):
        """初始化显示"""
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.title)

    def _init_fonts(self):
        """初始化字体"""
        try:
            self.font = pygame.font.Font("msyh.ttf", 36)
            self.title_font = pygame.font.Font("msyh.ttf", 48)
        except:
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 48)

    def _create_buttons(self):
        """创建按钮"""
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = self.screen_height // 2 - 80

        self.buttons = [
            Button("Start Game", 
                   (self.screen_width - button_width) // 2, 
                   start_y, 
                   button_width, button_height, 
                   color=GREEN, font=self.font),
            Button("History", 
                   (self.screen_width - button_width) // 2, 
                   start_y + button_height + button_spacing, 
                   button_width, button_height, 
                   color=BLUE, font=self.font),
            Button("Settings", 
                   (self.screen_width - button_width) // 2, 
                   start_y + 2 * (button_height + button_spacing), 
                   button_width, button_height, 
                   color=BLUE, font=self.font),
            Button("Quit", 
                   (self.screen_width - button_width) // 2, 
                   start_y + 3 * (button_height + button_spacing), 
                   button_width, button_height, 
                   color=RED, font=self.font)
        ]

    def run(self):
        """
        运行开始菜单
        
        :return: 用户选择 ("start", "history", "settings", "quit")
        """
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.choice = "quit"
                    self.running = False
                
                # 处理按钮事件
                for i, button in enumerate(self.buttons):
                    if button.handle_event(event):
                        choices = ["start", "history", "settings", "quit"]
                        self.choice = choices[i]
                        self.running = False

            self._draw()
            pygame.display.flip()
            clock.tick(60)
        
        return self.choice

    def _draw(self):
        """绘制菜单"""
        self.screen.fill(WHITE)
        
        # 绘制标题
        title_surface = self.title_font.render("Gomoku Game", True, BLACK)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(self.screen)

class ResultMenu:
    """结算菜单类"""
    def __init__(self, screen_width=400, screen_height=300, title="Game Result"):
        """
        初始化结算菜单
        
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :param title: 窗口标题
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.screen = None
        self.font = None
        
        self._init_display()
        self._init_fonts()

    def _init_display(self):
        """初始化显示"""
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.title)

    def _init_fonts(self):
        """初始化字体"""
        try:
            self.font = pygame.font.Font("msyh.ttf", 36)
        except:
            self.font = pygame.font.Font(None, 36)

    def read_result(self, filename="result.txt"):
        """
        读取结果文件
        
        :param filename: 结果文件名
        :return: 结果值
        :raises: FileNotFoundError
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"结果文件 {filename} 不存在")
        
        try:
            with open(filename, "r", encoding='utf-8') as file:
                return int(file.read().strip())
        except ValueError:
            raise ValueError("结果文件格式错误")

    def show_result(self, result=None, filename="result.txt", display_time=3000):
        """
        显示结算结果
        
        :param result: 直接传入的结果值，如果为None则从文件读取
        :param filename: 结果文件名
        :param display_time: 显示时间（毫秒）
        :return: bool，是否成功显示
        """
        try:
            if result is None:
                result = self.read_result(filename)
            
            # 根据结果显示不同的文本和颜色
            if result == 0:
                result_text = "You Lost!"
                text_color = RED
            elif result == 1:
                result_text = "You Won!"
                text_color = GREEN
            elif result == 2:
                result_text = "Draw!"
                text_color = BLUE
            else:
                result_text = "Unknown Result"
                text_color = BLACK

            # 绘制结果
            self.screen.fill(WHITE)
            text_surface = self.font.render(result_text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text_surface, text_rect)
            pygame.display.flip()
            
            # 等待指定时间
            pygame.time.wait(display_time)
            return True
            
        except (FileNotFoundError, ValueError) as e:
            print(f"显示结果失败: {e}")
            return False

class GameUI:
    """游戏UI管理类"""
    def __init__(self, screen_width=800, screen_height=600):
        """
        初始化游戏UI管理器
        
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.start_menu = None
        self.result_menu = None

    def show_start_menu(self, title="Gomoku Game"):
        """
        显示开始菜单
        
        :param title: 窗口标题
        :return: 用户选择 ("start", "settings", "quit")
        """
        self.start_menu = StartMenu(self.screen_width, self.screen_height, title)
        return self.start_menu.run()

    def show_result_menu(self, result=None, filename="result.txt", display_time=3000):
        """
        显示结算菜单
        
        :param result: 直接传入的结果值
        :param filename: 结果文件名
        :param display_time: 显示时间（毫秒）
        :return: bool，是否成功显示
        """
        self.result_menu = ResultMenu()
        return self.result_menu.show_result(result, filename, display_time)

    def quit(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()

    def get_screen_size(self):
        """
        获取屏幕尺寸
        
        :return: tuple，(width, height)
        """
        return (self.screen_width, self.screen_height)