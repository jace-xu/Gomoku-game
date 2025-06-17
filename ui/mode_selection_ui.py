import pygame
import sys

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BEIGE = (245, 245, 220)

class ModeSelectionUI:
    """游戏模式选择界面"""
    
    def __init__(self, screen_width=800, screen_height=600, screen=None):
        """
        初始化模式选择界面
        
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :param screen: 已存在的pygame screen对象
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = screen
        self.running = True
        self.choice = None
        
        # 保存原始窗口标题
        if self.screen:
            self.original_title = pygame.display.get_caption()[0]
            # 动态更新屏幕尺寸
            actual_size = self.screen.get_size()
            self.screen_width = actual_size[0]
            self.screen_height = actual_size[1]
        
        # 初始化字体
        self._init_fonts()
        
        # 加载背景
        self.background = None
        self._load_background()
    
    def _init_fonts(self):
        """初始化字体"""
        try:
            self.title_font = pygame.font.Font("msyh.ttf", 48)
            self.button_font = pygame.font.Font("msyh.ttf", 36)
        except (OSError, pygame.error):
            self.title_font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 36)
    
    def _load_background(self):
        """加载背景图片"""
        try:
            self.background = pygame.image.load("assets/loadbackground.jpg").convert()
            # 动态适应当前屏幕尺寸
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        except pygame.error:
            self.background = None
    
    def show(self):
        """
        显示模式选择界面
        
        :return: 用户选择 ("vs_ai", "vs_human", "back")
        """
        # 临时更改窗口标题
        if self.screen:
            pygame.display.set_caption("Select Game Mode")
        
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.choice = "back"
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.choice = "back"
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        mouse_pos = pygame.mouse.get_pos()
                        clicked_button = self._get_clicked_button(mouse_pos)
                        if clicked_button:
                            self.choice = clicked_button
                            self.running = False
            
            # 绘制界面
            self._draw()
            pygame.display.flip()
            clock.tick(60)
        
        # 恢复原始窗口标题
        if self.screen and hasattr(self, 'original_title'):
            pygame.display.set_caption(self.original_title)
        
        return self.choice
    
    def _draw(self):
        """绘制界面"""
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(WHITE)
        
        # 绘制标题
        title_text = self.title_font.render("Select Game Mode", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        self.screen.blit(title_text, title_rect)
        
        # 动态计算按钮位置和尺寸
        button_width = min(300, self.screen_width - 100)
        button_height = max(60, self.screen_height // 12)
        button_spacing = max(30, self.screen_height // 20)
        center_x = self.screen_width // 2
        start_y = self.screen_height // 2 - button_height - button_spacing // 2
        
        # VS AI 按钮
        vs_ai_rect = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        self._draw_button(vs_ai_rect, "VS AI", BEIGE)
        
        # VS Human 按钮
        vs_human_rect = pygame.Rect(center_x - button_width // 2, start_y + button_height + button_spacing, button_width, button_height)
        self._draw_button(vs_human_rect, "VS Human", BEIGE)
        
        # Back 按钮 - 动态定位
        back_width = min(120, self.screen_width // 6)
        back_height = min(50, self.screen_height // 12)
        back_rect = pygame.Rect(50, self.screen_height - back_height - 20, back_width, back_height)
        self._draw_button(back_rect, "Back", GRAY)
    
    def _draw_button(self, rect, text, color):
        """绘制按钮"""
        # 检查鼠标悬停
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            color = tuple(min(255, c + 30) for c in color)  # 悬停效果
        
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=12)
        
        button_text = self.button_font.render(text, True, BLACK)
        text_rect = button_text.get_rect(center=rect.center)
        self.screen.blit(button_text, text_rect)
    
    def _get_clicked_button(self, mouse_pos):
        """获取点击的按钮"""
        # 动态计算按钮位置（与_draw方法保持一致）
        button_width = min(300, self.screen_width - 100)
        button_height = max(60, self.screen_height // 12)
        button_spacing = max(30, self.screen_height // 20)
        center_x = self.screen_width // 2
        start_y = self.screen_height // 2 - button_height - button_spacing // 2
        
        # VS AI 按钮
        vs_ai_rect = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        if vs_ai_rect.collidepoint(mouse_pos):
            return "vs_ai"
        
        # VS Human 按钮
        vs_human_rect = pygame.Rect(center_x - button_width // 2, start_y + button_height + button_spacing, button_width, button_height)
        if vs_human_rect.collidepoint(mouse_pos):
            return "vs_human"
        
        # Back 按钮
        back_width = min(120, self.screen_width // 6)
        back_height = min(50, self.screen_height // 12)
        back_rect = pygame.Rect(50, self.screen_height - back_height - 20, back_width, back_height)
        if back_rect.collidepoint(mouse_pos):
            return "back"
        
        return None
