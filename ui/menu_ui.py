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

class Button:
    """按钮类"""
    def __init__(self, text, x, y, width, height, color, hover_color, font):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.hover = False
        self.font = font

    def draw(self, screen):
        if self.hover:
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            return True
        return False

class StartMenu:
    """开始菜单类"""
    def __init__(self, screen_width=800, screen_height=600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Gomoku Game Start Menu")
        
        # 加载支持中文的字体
        try:
            self.font = pygame.font.Font("msyh.ttf", 36)
        except:
            self.font = pygame.font.Font(None, 36)
        
        # 创建按钮
        self.start_button = Button("Start Game", 300, 200, 200, 50, GRAY, WHITE, self.font)
        self.settings_button = Button("Settings", 300, 300, 200, 50, GRAY, WHITE, self.font)
        
        self.running = True
        self.choice = None

    def run(self):
        """运行开始菜单"""
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.choice = "quit"
                    self.running = False
                
                # 处理按钮事件
                if self.start_button.handle_event(event):
                    self.choice = "start"
                    self.running = False
                    
                if self.settings_button.handle_event(event):
                    self.choice = "settings"
                    self.running = False

            # 绘制背景
            self.screen.fill(BLACK)

            # 绘制按钮
            self.start_button.draw(self.screen)
            self.settings_button.draw(self.screen)

            # 更新屏幕
            pygame.display.flip()
            clock.tick(60)
        
        return self.choice

class ResultMenu:
    """结算菜单类"""
    def __init__(self, screen_width=400, screen_height=300):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Game Result")
        
        # 加载支持中文的字体
        try:
            self.font = pygame.font.Font("msyh.ttf", 36)
        except:
            self.font = pygame.font.Font(None, 36)

    def read_result(self, filename="result.txt"):
        """读取结果文件"""
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return int(file.read().strip())
        else:
            raise FileNotFoundError("Result file not found")

    def show_result(self, result=None, filename="result.txt"):
        """显示结算结果"""
        # 如果没有直接传入结果，则从文件读取
        if result is None:
            try:
                result = self.read_result(filename)
            except FileNotFoundError as e:
                print(e)
                return False

        # 根据结果显示不同的文本
        if result == 0:
            result_text = "Game Lost!"
        elif result == 1:
            result_text = "Game Won!"
        else:
            result_text = "Unknown Result"

        # 渲染文本
        text_surface = self.font.render(result_text, True, WHITE)

        # 获取文本矩形
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # 绘制背景
        self.screen.fill(BLACK)

        # 绘制文本
        self.screen.blit(text_surface, text_rect)

        # 更新屏幕
        pygame.display.flip()

        # 等待一段时间
        pygame.time.wait(2000)
        
        return True

class GameUI:
    """游戏UI管理类"""
    def __init__(self):
        self.start_menu = StartMenu()
        self.result_menu = ResultMenu()

    def show_start_menu(self):
        """显示开始菜单"""
        return self.start_menu.run()

    def show_result_menu(self, result=None, filename="result.txt"):
        """显示结算菜单"""
        return self.result_menu.show_result(result, filename)

    def quit(self):
        """退出游戏"""
        pygame.quit()
        sys.exit()
'''
GameUI 类（主要接口类）
show_start_menu() - 显示开始菜单，返回用户选择（"start", "settings", "quit"）
show_result_menu(result=None, filename="result.txt") - 显示结算菜单
quit() - 退出游戏
StartMenu 类
run() - 运行开始菜单界面
ResultMenu 类
show_result(result=None, filename="result.txt") - 显示结算结果
read_result(filename="result.txt") - 从文件读取结果
'''