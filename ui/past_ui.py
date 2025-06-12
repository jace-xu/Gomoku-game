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
        self.font = pygame.font.SysFont('SimHei', 28)      # 标题字体
        self.small_font = pygame.font.SysFont('SimHei', 18) # 列表字体
        self.history_data = self.load_history_data()        # 历史对局数据列表
        self.scroll_offset = 0                              # 当前滚动偏移
        self.item_height = 130                              # 每条历史快照高度
        self.margin = 18                                    # 快照之间的间距
        
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
                    return data
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
        running = True
        clock = pygame.time.Clock()
        
        # 获取当前屏幕尺寸
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        while running:
            self.screen.fill(BG_COLOR)
            title = self.font.render("历史对局记录", True, FONT_COLOR)
            self.screen.blit(title, (screen_width // 2 - title.get_width() // 2, 20))

            # 事件处理：退出、滚动、按钮点击
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
                
                # 处理返回按钮点击
                if self.return_button.handle_event(event):
                    running = False
            
            # 显示历史记录数量
            if not self.history_data:
                no_data_text = self.font.render("暂无历史记录", True, FONT_COLOR)
                self.screen.blit(no_data_text, (screen_width // 2 - no_data_text.get_width() // 2, screen_height // 2))
            else:
                # 绘制每场对局快照
                start_y = 70 - self.scroll_offset
                for i, match in enumerate(self.history_data):
                    item_rect = pygame.Rect(40, start_y + i*self.item_height, screen_width-80, self.item_height - self.margin)
                    if item_rect.bottom > 60 and item_rect.top < screen_height:
                        try:
                            self.draw_match_snapshot(match, item_rect)
                        except Exception as snapshot_exc:
                            error_text = self.small_font.render(f"快照显示异常: {snapshot_exc}", True, (200, 50, 50))
                            self.screen.blit(error_text, (item_rect.x + 10, item_rect.y + 40))
            
            # 绘制返回按钮
            self.return_button.draw(self.screen)
            
            # 绘制操作提示
            hint_text = self.small_font.render("提示: 使用方向键或鼠标滚轮滚动，ESC或点击返回按钮退出", True, (100, 100, 100))
            self.screen.blit(hint_text, (10, screen_height - 25))
            
            pygame.display.flip()
            clock.tick(60)

    def draw_match_snapshot(self, match_data: Dict, rect: pygame.Rect) -> None:
        """
        绘制单场对局快照
        包括时间戳、评语、棋盘快照、落子数等

        :param match_data: 单场对局的数据字典
        :param rect: pygame.Rect 对象，快照绘制区域
        :return: None
        """
        try:
            # 绘制快照背景框
            pygame.draw.rect(self.screen, (220, 220, 220), rect, border_radius=8)
            # 显示时间戳
            ts = match_data.get('timestamp', '未知时间')
            ts_text = self.small_font.render(f"时间: {ts}", True, FONT_COLOR)
            self.screen.blit(ts_text, (rect.x + 10, rect.y + 10))

            # 显示对局评语
            comment = match_data.get('comment', '')
            cm_text = self.small_font.render(f"评语: {comment}", True, FONT_COLOR)
            self.screen.blit(cm_text, (rect.x + 200, rect.y + 10))

            # 棋盘快照（小型棋盘）
            board_state = match_data.get('board', None)
            if isinstance(board_state, list):
                self._draw_board_snapshot(board_state, rect.x + 20, rect.y + 40, size=70)
            # 落子数
            moves = len(match_data.get('moves', []))
            mv_text = self.small_font.render(f"落子数: {moves}", True, FONT_COLOR)
            self.screen.blit(mv_text, (rect.x + 400, rect.y + 45))
        except Exception as exc:
            # 单场快照绘制异常，绘制错误提示
            error_text = self.small_font.render(f"快照异常: {exc}", True, (200, 50, 50))
            self.screen.blit(error_text, (rect.x + 10, rect.y + 40))

    def _draw_board_snapshot(self, board_state: List[List[int]], x: int, y: int, size: int = 70) -> None:
        """
        绘制棋盘快照（小棋盘）

        :param board_state: 2D列表，0空位，1黑子，2白子
        :param x: 棋盘左上角x坐标
        :param y: 棋盘左上角y坐标
        :param size: 棋盘整体尺寸（正方形）
        :return: None
        """
        if not isinstance(board_state, list) or not board_state:
            # 确保类型是 list[list[int]]，否则直接返回
            return
        rows = len(board_state)
        cols = len(board_state[0]) if rows else 0
        cell = size // max(rows, cols, 1)
        for i in range(rows):
            for j in range(cols):
                rect = pygame.Rect(x + j * cell, y + i * cell, cell, cell)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
                if board_state[i][j] == 1:
                    # 黑子
                    pygame.draw.circle(self.screen, (30, 30, 30), rect.center, cell // 3)
                elif board_state[i][j] == 2:
                    # 白子
                    pygame.draw.circle(self.screen, (220, 220, 220), rect.center, cell // 3)

    def run(self) -> None:
        """
        入口接口：主菜单跳转到历史记录界面时调用本方法

        :return: None
        """
        try:
            self.draw_history_view()
        except Exception as run_exc:
            print(f"历史记录界面异常: {run_exc}")

