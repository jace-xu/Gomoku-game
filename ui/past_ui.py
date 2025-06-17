import os
import json
import pygame
from typing import List, Dict

# 历史记录文件路径（使用相对路径）
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'game_database', 'history.json')
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (245, 245, 245)
FONT_COLOR = (30, 30, 30)
SCROLL_SPEED = 30  # 滚动时每次移动的像素数

class Button:
    """简单的按钮类"""
    def __init__(self, text, x, y, width, height, color=(100, 100, 100), text_color=(255, 255, 255)):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.hover = False
        
    def draw(self, screen):
        # 悬停效果
        current_color = tuple(min(255, c + 30) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # 边框
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hover and event.button == 1:
            return True
        return False

class GameDetailUI:
    """游戏详细记录查看界面"""
    
    def __init__(self, screen: pygame.Surface, game_data: Dict):
        self.screen = screen
        self.game_data = game_data
        
        # 使用统一的字体初始化方式
        self._init_fonts()
        
        # 保存原始窗口标题，退出时恢复
        self.original_title = pygame.display.get_caption()[0]
        
        # 创建返回按钮
        self.return_button = Button("Back", 10, 10, 80, 35, (70, 130, 180))
        
        # 动态计算布局
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # 棋盘显示区域（动态调整）
        self.board_size = min(180, self.screen_width // 4)  # 动态调整棋盘大小
        self.board_x = 30
        self.board_y = 60
        
        # 信息显示区域（动态调整）
        self.info_x = self.board_x + self.board_size + 20
        self.info_y = self.board_y

    def _init_fonts(self):
        """初始化字体，使用与其他UI组件一致的方式"""
        try:
            # 首先尝试加载中文字体
            self.font = pygame.font.Font("msyh.ttf", 24)
            self.small_font = pygame.font.Font("msyh.ttf", 18)
            self.title_font = pygame.font.Font("msyh.ttf", 32)
        except (OSError, pygame.error):
            # 如果中文字体加载失败，使用默认字体
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 32)
    
    def run(self):
        """运行详细记录查看界面"""
        # 临时更改窗口标题
        pygame.display.set_caption("Game Details")
        
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
                # 处理返回按钮点击
                if self.return_button.handle_event(event):
                    running = False
            
            # 完全清除屏幕并重绘
            self.screen.fill(BG_COLOR)
            self._draw_detail_view()
            pygame.display.flip()
            clock.tick(60)
        
        # 恢复原始窗口标题
        pygame.display.set_caption(self.original_title)

    def _draw_detail_view(self):
        """绘制详细记录视图"""
        # 不需要再次填充背景，因为在run()中已经清除了
        
        # 绘制标题
        title = self.title_font.render("Game Details", True, FONT_COLOR)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 15))
        
        # 绘制返回按钮
        self.return_button.draw(self.screen)
        
        # 绘制棋盘
        self._draw_large_board()
        
        # 绘制游戏信息
        self._draw_game_info()
        
        # 绘制评语
        self._draw_comment()
    
    def _draw_large_board(self):
        """绘制大棋盘"""
        board_state = self.game_data.get('board', [])
        if not board_state:
            return
        
        # 绘制背景
        board_rect = pygame.Rect(self.board_x, self.board_y, self.board_size, self.board_size)
        pygame.draw.rect(self.screen, (240, 217, 181), board_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), board_rect, 2)
        
        board_len = len(board_state)
        if board_len == 0:
            return
        
        cell_size = self.board_size // board_len
        
        # 绘制网格线
        for i in range(board_len):
            # 水平线
            start_x = self.board_x
            start_y = self.board_y + i * cell_size
            end_x = self.board_x + self.board_size
            pygame.draw.line(self.screen, (100, 100, 100), (start_x, start_y), (end_x, start_y), 1)
            
            # 垂直线
            start_x = self.board_x + i * cell_size
            start_y = self.board_y
            end_y = self.board_y + self.board_size
            pygame.draw.line(self.screen, (100, 100, 100), (start_x, start_y), (start_x, end_y), 1)
        
        # 绘制棋子
        for i in range(board_len):
            for j in range(len(board_state[i])):
                piece = board_state[i][j]
                if piece == 0:
                    continue
                
                center_x = self.board_x + j * cell_size + cell_size // 2
                center_y = self.board_y + i * cell_size + cell_size // 2
                radius = max(3, cell_size // 3)
                
                if piece == 1:  # 黑子
                    pygame.draw.circle(self.screen, (30, 30, 30), (center_x, center_y), radius)
                elif piece == 2:  # 白子
                    pygame.draw.circle(self.screen, (220, 220, 220), (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, (0, 0, 0), (center_x, center_y), radius, 1)
    
    def _draw_game_info(self):
        """绘制游戏信息"""
        y_offset = self.info_y
        line_height = 25
        
        # 时间
        timestamp = self.game_data.get('timestamp', 'Unknown Time')
        time_text = self.font.render(f"Time: {timestamp}", True, FONT_COLOR)
        self.screen.blit(time_text, (self.info_x, y_offset))
        y_offset += line_height
        
        # 游戏模式
        game_mode = self.game_data.get('game_mode', 'vs_ai')
        mode_text = "VS AI" if game_mode == "vs_ai" else "VS Human"
        mode_surface = self.font.render(f"Mode: {mode_text}", True, FONT_COLOR)
        self.screen.blit(mode_surface, (self.info_x, y_offset))
        y_offset += line_height
        
        # 游戏结果
        result = self.game_data.get('result', None)
        if result is not None:
            if game_mode == "vs_human":
                # 双人对战模式
                if result == 1:
                    result_text = "Result: Black Won"
                    result_color = (0, 150, 0)
                elif result == 0:
                    result_text = "Result: White Won"
                    result_color = (150, 0, 0)
                elif result == 2:
                    result_text = "Result: Draw"
                    result_color = (0, 0, 150)
                else:
                    result_text = "Result: Unknown"
                    result_color = FONT_COLOR
            else:
                # AI对战模式
                if result == 1:
                    result_text = "Result: Human Won"
                    result_color = (0, 150, 0)
                elif result == 0:
                    result_text = "Result: AI Won"
                    result_color = (150, 0, 0)
                elif result == 2:
                    result_text = "Result: Draw"
                    result_color = (0, 0, 150)
                else:
                    result_text = "Result: Unknown"
                    result_color = FONT_COLOR
            
            result_surface = self.font.render(result_text, True, result_color)
            self.screen.blit(result_surface, (self.info_x, y_offset))
            y_offset += line_height
        
        # 落子数
        moves = len(self.game_data.get('moves', []))
        moves_text = self.font.render(f"Total Moves: {moves}", True, FONT_COLOR)
        self.screen.blit(moves_text, (self.info_x, y_offset))
        y_offset += line_height * 2
        
        # 分割线
        pygame.draw.line(self.screen, FONT_COLOR, 
                        (self.info_x, y_offset), 
                        (self.screen_width - 50, y_offset), 2)
    
    def _draw_comment(self):
        """绘制评语"""
        # 增加评语起始位置的Y坐标，避免与上方信息重叠
        comment_y = self.info_y + 150  # 从120增加到150，增加30像素间距
        
        # 评语标题
        comment_title = self.font.render("AI Commentary:", True, FONT_COLOR)
        self.screen.blit(comment_title, (self.info_x, comment_y))
        comment_y += 35  # 从30增加到35，标题与内容间距稍微增加
        
        # 评语内容
        comment = self.game_data.get('comment', 'No commentary available')
        if comment == "评语生成中...":
            comment = "Commentary generation failed, but this was an exciting game!"
        
        # 多行显示评语（增加显示宽度）
        max_width = self.screen_width - self.info_x - 20  # 减少右边距，增加显示宽度
        self._draw_multiline_text(comment, self.info_x, comment_y, max_width)
    
    def _draw_multiline_text(self, text, x, y, max_width):
        """绘制多行文本"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.small_font.render(test_line, True, FONT_COLOR)
            
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
        
        line_height = self.small_font.get_height() + 3
        for i, line in enumerate(lines):
            line_surface = self.small_font.render(line, True, FONT_COLOR)
            self.screen.blit(line_surface, (x, y + i * line_height))

class HistoryUI:
    """
    历史对局记录界面类，实现历史数据加载、浏览和对局快照绘制功能，
    并提供run方法作为主菜单跳转入口。
    """

    def __init__(self, disp_surface: pygame.Surface) -> None:
        """
        初始化历史记录界面

        :param disp_surface: pygame 窗口对象，由主程序提供
        :return: None
        """
        self.screen = disp_surface
        self.font = pygame.font.Font(None, 28)      # 标题字体
        self.small_font = pygame.font.Font(None, 16) # 列表字体
        self.history_data = self.load_history_data()        # 历史对局数据列表
        self.scroll_offset = 0                              # 当前滚动偏移
        self.item_height = 120                              # 每条历史快照高度（增加以容纳三行）
        self.margin = 15                                    # 快照之间的间距
        
        # 保存原始窗口标题，退出时恢复
        self.original_title = pygame.display.get_caption()[0]
        
        # 创建返回按钮
        self.return_button = Button("Back", 10, 10, 100, 40, (70, 130, 180))

    @staticmethod
    def load_history_data() -> List[Dict]:
        """
        加载历史对局数据
        从 JSON 文件中读取历史对局数据，文件不存在或出错时返回空列表。

        :return: 历史对局数据列表，每项为字典（包含棋盘状态、评语、时间戳、落子记录等）
        """
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # 按时间倒序排列，最新的在前面
                    return sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)
                else:
                    print("历史记录文件不是列表格式。")
        except json.JSONDecodeError as json_err:
            print(f"历史记录文件格式错误，无法解析JSON：{json_err}")
        except OSError as os_err:
            print(f"无法访问历史记录文件：{os_err}")
        except Exception as unknown_err:
            print(f"加载历史记录时发生未知错误: {unknown_err}")
        return []

    def draw_history_view(self) -> None:
        """
        绘制历史记录主界面
        支持上下滚动浏览历史，ESC键或关闭窗口可退出历史记录界面。
        鼠标滚轮及上下方向键控制滚动。

        :return: None
        """
        # 临时更改窗口标题
        pygame.display.set_caption("Game History")
        
        running = True
        clock = pygame.time.Clock()
        
        # 获取当前屏幕尺寸
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        while running:
            # 完全清除屏幕
            self.screen.fill(BG_COLOR)
            
            # 绘制标题
            title = self.font.render("Game History", True, FONT_COLOR)
            self.screen.blit(title, (screen_width // 2 - title.get_width() // 2, 20))

            # 事件处理：退出、滚动、按钮点击、项目点击
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_DOWN:
                        self.scroll_offset = min(
                            self.scroll_offset + SCROLL_SPEED,
                            max(0, len(self.history_data) * self.item_height - (screen_height - 80))
                        )
                    elif event.key == pygame.K_UP:
                        self.scroll_offset = max(self.scroll_offset - SCROLL_SPEED, 0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # 滚轮上
                        self.scroll_offset = max(self.scroll_offset - SCROLL_SPEED, 0)
                    elif event.button == 5:  # 滚轮下
                        self.scroll_offset = min(
                            self.scroll_offset + SCROLL_SPEED,
                            max(0, len(self.history_data) * self.item_height - (screen_height - 80))
                        )
                    elif event.button == 1:  # 左键点击
                        # 检查是否点击了历史记录项
                        clicked_index = self._get_clicked_item(event.pos)
                        if clicked_index is not None:
                            # 显示详细记录
                            detail_ui = GameDetailUI(self.screen, self.history_data[clicked_index])
                            detail_ui.run()
                
                # 处理返回按钮点击
                if self.return_button.handle_event(event):
                    running = False
            
            # 显示历史记录数量
            if not self.history_data:
                no_data_text = self.font.render("No game history available", True, FONT_COLOR)
                self.screen.blit(no_data_text, (screen_width // 2 - no_data_text.get_width() // 2, screen_height // 2))
            else:
                # 绘制每场对局快照
                start_y = 70 - self.scroll_offset
                for i, match in enumerate(self.history_data):
                    item_rect = pygame.Rect(40, start_y + i*self.item_height, screen_width-80, self.item_height - self.margin)
                    if item_rect.bottom > 60 and item_rect.top < screen_height:
                        try:
                            self.draw_match_snapshot(match, item_rect, i)
                        except Exception as snapshot_exc:
                            error_text = self.small_font.render(f"快照显示异常: {snapshot_exc}", True, (200, 50, 50))
                            self.screen.blit(error_text, (item_rect.x + 10, item_rect.y + 40))
            
            # 绘制返回按钮
            self.return_button.draw(self.screen)
            
            # 绘制操作提示
            hint_text = self.small_font.render("Tip: Click record to view details, arrow keys or mouse wheel to scroll, ESC to return", True, (100, 100, 100))
            self.screen.blit(hint_text, (10, screen_height - 25))
            
            pygame.display.flip()
            clock.tick(60)
        
        # 恢复原始窗口标题
        pygame.display.set_caption(self.original_title)

    def _get_clicked_item(self, mouse_pos):
        """获取点击的历史记录项索引"""
        if not self.history_data:
            return None
        
        screen_width = self.screen.get_width()
        start_y = 70 - self.scroll_offset
        
        for i in range(len(self.history_data)):
            item_rect = pygame.Rect(40, start_y + i*self.item_height, screen_width-80, self.item_height - self.margin)
            if item_rect.collidepoint(mouse_pos):
                return i
        return None

    def draw_match_snapshot(self, match_data: Dict, rect: pygame.Rect, index: int) -> None:
        """
        绘制单场对局快照
        包括时间戳、评语摘要、棋盘快照、落子数等

        :param match_data: 单场对局的数据字典
        :param rect: pygame.Rect 对象，快照绘制区域
        :param index: 记录索引
        :return: None
        """
        try:
            # 绘制快照背景框（带点击效果）
            pygame.draw.rect(self.screen, (230, 230, 230), rect, border_radius=5)
            pygame.draw.rect(self.screen, (180, 180, 180), rect, 1, border_radius=5)
            
            # 第一行：时间戳和游戏模式
            ts = match_data.get('timestamp', 'Unknown Time')
            ts_text = self.small_font.render(f"Time: {ts}", True, FONT_COLOR)
            self.screen.blit(ts_text, (rect.x + 10, rect.y + 8))

            # 显示游戏模式
            game_mode = match_data.get('game_mode', 'vs_ai')
            mode_text = "VS AI" if game_mode == "vs_ai" else "VS Human"
            mode_surface = self.small_font.render(mode_text, True, (100, 100, 100))
            self.screen.blit(mode_surface, (rect.x + 250, rect.y + 8))

            # 显示游戏结果（在第一行右侧）
            result = match_data.get('result', None)
            if result is not None:
                if game_mode == "vs_human":
                    # 双人对战模式
                    if result == 1:
                        result_text = "Black Won"
                        result_color = (0, 150, 0)
                    elif result == 0:
                        result_text = "White Won"
                        result_color = (150, 0, 0)
                    elif result == 2:
                        result_text = "Draw"
                        result_color = (0, 0, 150)
                    else:
                        result_text = "Unknown"
                        result_color = FONT_COLOR
                else:
                    # AI对战模式
                    if result == 1:
                        result_text = "Human Won"
                        result_color = (0, 150, 0)
                    elif result == 0:
                        result_text = "AI Won"
                        result_color = (150, 0, 0)
                    elif result == 2:
                        result_text = "Draw"
                        result_color = (0, 0, 150)
                    else:
                        result_text = "Unknown"
                        result_color = FONT_COLOR
                
                result_surface = self.small_font.render(result_text, True, result_color)
                self.screen.blit(result_surface, (rect.x + 350, rect.y + 8))

            # 第二行：评语摘要
            comment = match_data.get('comment', 'No commentary available')
            if comment == "评语生成中...":
                comment = "Commentary generation failed"
            
            comment_summary = comment[:50] + "..." if len(comment) > 50 else comment
            cm_text = self.small_font.render(f"Comment: {comment_summary}", True, FONT_COLOR)
            self.screen.blit(cm_text, (rect.x + 10, rect.y + 30))

            # 第三行：步数
            moves = len(match_data.get('moves', []))
            mv_text = self.small_font.render(f"Moves: {moves}", True, FONT_COLOR)
            self.screen.blit(mv_text, (rect.x + 10, rect.y + 52))

            # 棋盘快照（小型棋盘）- 放在左下角
            board_state = match_data.get('board', None)
            if isinstance(board_state, list):
                self._draw_board_snapshot(board_state, rect.x + 15, rect.y + 75, size=40)
            
            # 点击提示（右下角）
            click_hint = self.small_font.render("Click for details ->", True, (100, 100, 100))
            self.screen.blit(click_hint, (rect.x + rect.width - 120, rect.y + rect.height - 20))
            
        except Exception as exc:
            # 单场快照绘制异常，绘制错误提示
            error_text = self.small_font.render(f"Snapshot error: {exc}", True, (200, 50, 50))
            self.screen.blit(error_text, (rect.x + 10, rect.y + 40))

    def _draw_board_snapshot(self, board_state: List[List[int]], x: int, y: int, size: int = 40) -> None:
        """
        绘制棋盘快照（小棋盘）

        :param board_state: 2D列表，0空位，1黑子，2白子
        :param x: 棋盘左上角x坐标
        :param y: 棋盘左上角y坐标
        :param size: 棋盘整体尺寸（正方形）
        :return: None
        """
        if not isinstance(board_state, list) or not board_state:
            return
            
        rows = len(board_state)
        cols = len(board_state[0]) if rows else 0
        cell = size // max(rows, cols, 1)
        
        # 绘制棋盘背景
        board_rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(self.screen, (240, 217, 181), board_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), board_rect, 1)
        
        for i in range(rows):
            for j in range(cols):
                center_x = x + j * cell + cell // 2
                center_y = y + i * cell + cell // 2
                radius = max(1, cell // 4)
                
                if board_state[i][j] == 1:
                    # 黑子
                    pygame.draw.circle(self.screen, (30, 30, 30), (center_x, center_y), radius)
                elif board_state[i][j] == 2:
                    # 白子
                    pygame.draw.circle(self.screen, (220, 220, 220), (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, (100, 100, 100), (center_x, center_y), radius, 1)

    def run(self) -> None:
        """
        入口接口：主菜单跳转到历史记录界面时调用本方法

        :return: None
        """
        try:
            self.draw_history_view()
        except Exception as run_exc:
            print(f"History UI error: {run_exc}")

