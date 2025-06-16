import pygame
import sys
import os
import json

# 初始化 pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BEIGE = (245, 245, 220)  # 米白色

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
    def __init__(self, screen_width=800, screen_height=600, title="Gomoku Game", background_image="assets/loadbackground.jpg", screen=None):
        """
        初始化开始菜单
        
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :param title: 窗口标题
        :param background_image: 背景图片路径
        :param screen: 已存在的pygame screen对象，如果提供则重用，否则创建新的
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.screen = screen
        self.font = None
        self.title_font = None
        self.buttons = []
        self.running = True
        self.choice = None
        self.background_image = background_image
        self.background = None
        self.should_create_display = screen is None  # 标记是否需要创建新显示
        
        if self.should_create_display:
            self._init_display()
        else:
            # 保存原始窗口标题，退出时恢复
            self.original_title = pygame.display.get_caption()[0]
        
        self._init_fonts()
        self._load_background()
        self._create_buttons()

    def _init_display(self):
        """初始化显示"""
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.title)

    def _init_fonts(self):
        """初始化字体，使用统一的字体加载方式"""
        try:
            # 首先尝试加载中文字体
            self.font = pygame.font.Font("msyh.ttf", 36)
            self.title_font = pygame.font.Font("msyh.ttf", 48)
        except (OSError, pygame.error):
            # 如果中文字体加载失败，使用默认字体
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
                   color=BEIGE, text_color=BLACK, font=self.font),
            Button("History", 
                   (self.screen_width - button_width) // 2, 
                   start_y + button_height + button_spacing, 
                   button_width, button_height, 
                   color=BEIGE, text_color=BLACK, font=self.font),
            Button("Settings", 
                   (self.screen_width - button_width) // 2, 
                   start_y + 2 * (button_height + button_spacing), 
                   button_width, button_height, 
                   color=BEIGE, text_color=BLACK, font=self.font),
            Button("Quit", 
                   (self.screen_width - button_width) // 2, 
                   start_y + 3 * (button_height + button_spacing), 
                   button_width, button_height, 
                   color=BEIGE, text_color=BLACK, font=self.font)
        ]

    def _load_background(self):
        """加载背景图片"""
        try:
            self.background = pygame.image.load(self.background_image).convert()
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        except pygame.error as e:
            print(f"加载背景图片失败: {e}")
            self.background = None

    def run(self):
        """
        运行开始菜单
        
        :return: 用户选择 ("start", "history", "settings", "quit")
        """
        # 如果重用现有screen，临时更改窗口标题
        if not self.should_create_display:
            pygame.display.set_caption(self.title)
        
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

            # 完全清除屏幕并重绘
            self._draw()
            pygame.display.flip()
            clock.tick(60)
        
        # 如果重用现有screen，恢复原始窗口标题
        if not self.should_create_display and hasattr(self, 'original_title'):
            pygame.display.set_caption(self.original_title)
        
        return self.choice

    def _draw(self):
        """绘制菜单"""
        # 确保完全清除之前的内容
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
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
    def __init__(self, screen_width=600, screen_height=500, title="Game Result"):
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
        self.small_font = None
        
        self._init_display()
        self._init_fonts()

    def _init_display(self):
        """初始化显示"""
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(self.title)

    def _init_fonts(self):
        """初始化字体"""
        try:
            self.font = pygame.font.Font("msyh.ttf", 32)
            self.small_font = pygame.font.Font("msyh.ttf", 20)
        except:
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)

    def read_result(self, results_file=None):
        """
        从JSON文件读取最新的游戏结果
        
        :param results_file: 结果文件路径，如果为None则使用默认路径
        :return: 结果值
        :raises: FileNotFoundError
        """
        if results_file is None:
            # 使用相对路径
            results_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'game_database', 
                'results.json'
            )
        
        if not os.path.exists(results_file):
            raise FileNotFoundError(f"结果文件 {results_file} 不存在")
        
        try:
            with open(results_file, "r", encoding='utf-8') as file:
                results_data = json.load(file)
                
            if isinstance(results_data, list) and results_data:
                # 返回最新（最后一个）结果
                return results_data[-1]['result']
            else:
                raise ValueError("结果文件格式错误或为空")
                
        except json.JSONDecodeError:
            raise ValueError("结果文件JSON格式错误")

    def show_result(self, result=None, results_file=None, display_time=3000):
        """
        显示结算结果
        
        :param result: 直接传入的结果值，如果为None则从文件读取
        :param results_file: 结果文件路径
        :param display_time: 显示时间（毫秒）
        :return: bool，是否成功显示
        """
        try:
            if result is None:
                result = self.read_result(results_file)
            
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

    def show_result_with_comment(self, result=None, comment="精彩的对弈！", results_file=None):
        """
        显示结算结果和评语，等待用户点击确认按钮
        
        :param result: 直接传入的结果值，如果为None则从文件读取
        :param comment: 对局评语
        :param results_file: 结果文件路径
        :return: bool，用户是否确认
        """
        try:
            if result is None:
                result = self.read_result(results_file)
            
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

            # 创建确认按钮 - 使用英文字体避免乱码
            confirm_button = Button(
                "Back", 
                self.screen_width // 2 - 60, 
                self.screen_height - 80, 
                120, 50, 
                color=GRAY, 
                font=pygame.font.Font(None, 32)  # 使用默认字体避免中文显示问题
            )
            
            # 显示界面直到用户点击确认
            clock = pygame.time.Clock()
            confirmed = False
            
            while not confirmed:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return True  # 强制关闭时返回True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            confirmed = True
                    
                    # 处理按钮事件
                    if confirm_button.handle_event(event):
                        confirmed = True
                
                # 绘制界面
                self.screen.fill(WHITE)
                
                # 绘制结果文本
                result_surface = self.font.render(result_text, True, text_color)
                result_rect = result_surface.get_rect(center=(self.screen_width // 2, 80))
                self.screen.blit(result_surface, result_rect)
                
                # 绘制评语标题
                comment_title = self.small_font.render("Comments from Deepseek:", True, BLACK)
                self.screen.blit(comment_title, (50, 130))
                
                # 绘制评语内容（支持多行显示）
                self._draw_multiline_text(comment, 50, 160, self.screen_width - 100, self.small_font, BLACK)
                
                # 绘制确认按钮
                confirm_button.draw(self.screen)
                
                pygame.display.flip()
                clock.tick(60)
            
            return True
            
        except (FileNotFoundError, ValueError) as e:
            print(f"显示结果失败: {e}")
            return False

    def show_result_with_async_comment(self, result=None, board_state=None, move_history=None, commentator=None, results_file=None):
        """
        显示结算结果和异步生成的评语，带打字机效果
        
        :param result: 直接传入的结果值，如果为None则从文件读取
        :param board_state: 棋盘状态（用于生成评语）
        :param move_history: 落子历史（用于生成评语）
        :param commentator: 评语生成器实例
        :param results_file: 结果文件路径
        :return: tuple，(用户是否确认, 生成的评语)
        """
        try:
            if result is None:
                result = self.read_result(results_file)
            
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

            # 创建确认按钮
            confirm_button = Button(
                "Back", 
                self.screen_width // 2 - 60, 
                self.screen_height - 80, 
                120, 50, 
                color=GRAY, 
                font=pygame.font.Font(None, 32)
            )
            
            # 评语相关变量
            comment_text = ""
            full_comment = ""
            comment_generating = True
            comment_display_index = 0
            typing_speed = 10  # 基础打字速度（每秒字符数）
            last_char_time = 0
            typing_interval = 50  # 初始打字间隔（毫秒）
            comment_thread = None
            generated_comment = None  # 存储生成的评语
            
            # 启动评语生成线程
            import threading
            def generate_comment():
                nonlocal full_comment, comment_generating, typing_interval, generated_comment
                try:
                    if commentator and board_state and move_history:
                        generated_comment = commentator.generate_comment(board_state, move_history, result)
                        full_comment = generated_comment
                    else:
                        generated_comment = "Excellent game! Well played!"
                        full_comment = generated_comment
                except Exception as e:
                    print(f"评语生成失败: {e}")
                    generated_comment = "Commentary generation failed, but this was an exciting game!"
                    full_comment = generated_comment
                
                # 根据评语长度动态调整打字速度，目标5秒显示完成
                if full_comment:
                    target_time = 5.0  # 目标显示时间（秒）
                    typing_interval = max(20, int((target_time * 1000) / len(full_comment)))  # 计算每个字符的间隔
                
                comment_generating = False
            
            comment_thread = threading.Thread(target=generate_comment)
            comment_thread.daemon = True
            comment_thread.start()
            
            # 显示界面直到用户点击确认
            clock = pygame.time.Clock()
            confirmed = False
            
            while not confirmed:
                current_time = pygame.time.get_ticks()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # 确保线程结束
                        if comment_thread and comment_thread.is_alive():
                            comment_thread.join(timeout=0.1)
                        return True, generated_comment  # 返回生成的评语
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            confirmed = True
                    
                    # 处理按钮事件
                    if confirm_button.handle_event(event):
                        confirmed = True
                
                # 更新评语显示
                if comment_generating:
                    # 显示生成中状态
                    dots = "." * ((current_time // 500) % 4)  # 动态省略号
                    comment_text = f"AI is thinking{dots}"
                else:
                    # 打字机效果显示评语
                    if comment_display_index < len(full_comment):
                        if current_time - last_char_time > typing_interval:
                            comment_display_index += 1
                            last_char_time = current_time
                    comment_text = full_comment[:comment_display_index]
                
                # 绘制界面
                self.screen.fill(WHITE)
                
                # 绘制结果文本
                result_surface = self.font.render(result_text, True, text_color)
                result_rect = result_surface.get_rect(center=(self.screen_width // 2, 80))
                self.screen.blit(result_surface, result_rect)
                
                # 绘制评语标题
                comment_title = self.small_font.render("Comments from Deepseek:", True, BLACK)
                self.screen.blit(comment_title, (50, 130))
                
                # 绘制评语内容（支持多行显示和打字机效果）
                self._draw_multiline_text_with_typing(comment_text, 50, 160, self.screen_width - 100, self.small_font, BLACK)
                
                # 绘制确认按钮
                confirm_button.draw(self.screen)
                
                pygame.display.flip()
                clock.tick(60)
            
            # 确保线程结束
            if comment_thread and comment_thread.is_alive():
                comment_thread.join(timeout=0.1)
            
            return True, generated_comment  # 返回生成的评语
            
        except (FileNotFoundError, ValueError) as e:
            print(f"显示结果失败: {e}")
            return False, None

    def _draw_multiline_text(self, text, x, y, max_width, font, color):
        """
        绘制多行文本
        
        :param text: 要绘制的文本
        :param x: 起始x坐标
        :param y: 起始y坐标
        :param max_width: 最大宽度
        :param font: 字体对象
        :param color: 文本颜色
        """
        if not text:
            return
            
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = font.get_height() + 5
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            self.screen.blit(line_surface, (x, y + i * line_height))

    def _draw_multiline_text_with_typing(self, text, x, y, max_width, font, color):
        """
        绘制多行文本，支持打字机效果
        
        :param text: 要绘制的文本
        :param x: 起始x坐标
        :param y: 起始y坐标
        :param max_width: 最大宽度
        :param font: 字体对象
        :param color: 文本颜色
        """
        if not text:
            return
            
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = font.get_height() + 5
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            self.screen.blit(line_surface, (x, y + i * line_height))

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

    def show_settings_menu(self, screen, move_logic, board_ui, assets_path="assets", background_image="assets/loadbackground.jpg"):
        """
        显示设置菜单
        
        :param screen: pygame窗口Surface对象
        :param move_logic: 游戏逻辑对象
        :param board_ui: 棋盘UI对象
        :param assets_path: 资源文件夹路径
        :param background_image: 背景图片路径
        :return: bool，用户是否正常退出设置界面
        """
        try:
            from ui.setting_ui import SettingUI
            setting_ui = SettingUI(
                screen=screen,
                move_logic=move_logic,
                board_ui=board_ui,
                assets_path=assets_path,
                background_image=background_image
            )
            setting_ui.show()
            return True
        except Exception as e:
            print(f"显示设置界面失败: {e}")
            return False

    def show_result_menu(self, result=None, results_file=None, display_time=3000):
        """
        显示结算菜单
        
        :param result: 直接传入的结果值
        :param results_file: 结果文件路径
        :param display_time: 显示时间（毫秒）
        :return: bool，是否成功显示
        """
        self.result_menu = ResultMenu()
        return self.result_menu.show_result(result, results_file, display_time)

    def show_result_menu_with_comment(self, result=None, comment="精彩的对弈！", results_file=None):
        """
        显示带评语的结算菜单
        
        :param result: 直接传入的结果值
        :param comment: 对局评语
        :param results_file: 结果文件路径
        :return: bool，用户是否确认
        """
        self.result_menu = ResultMenu()
        return self.result_menu.show_result_with_comment(result, comment, results_file)

    def show_result_menu_with_async_comment(self, result=None, board_state=None, move_history=None, commentator=None, results_file=None):
        """
        显示带异步评语生成的结算菜单
        
        :param result: 直接传入的结果值
        :param board_state: 棋盘状态
        :param move_history: 落子历史
        :param commentator: 评语生成器
        :param results_file: 结果文件路径
        :return: tuple，(用户是否确认, 生成的评语)
        """
        self.result_menu = ResultMenu()
        return self.result_menu.show_result_with_async_comment(result, board_state, move_history, commentator, results_file)

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