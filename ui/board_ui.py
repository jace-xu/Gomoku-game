import pygame

class BoardUI:
    def __init__(self, screen, board_size=15, grid_size=40, margin=None, background_color=(255, 255, 255)):
        """
        初始化棋盘UI。
        
        :param screen: pygame 的主窗口
        :param board_size: 棋盘大小(格子数,默认15)
        :param grid_size: 每格像素大小,默认40
        :param margin: 边距，如果为None则等于grid_size
        :param background_color: 背景颜色
        """
        self.screen = screen
        self.board_size = board_size
        self.grid_size = grid_size
        self.margin = margin if margin is not None else grid_size
        self.background_color = background_color
        self.piece_radius = grid_size // 2 - 4
        self.board_pixel_size = board_size * grid_size
        
        # 计算实际需要的屏幕尺寸
        self.total_width = self.board_pixel_size + 2 * self.margin
        self.total_height = self.board_pixel_size + 2 * self.margin
        
        # 线条和棋子颜色
        self.line_color = (0, 0, 0)
        self.black_piece_color = (0, 0, 0)
        self.white_piece_color = (255, 255, 255)
        self.piece_border_color = (0, 0, 0)

    def get_required_size(self):
        """
        获取棋盘UI所需的最小屏幕尺寸
        
        :return: tuple，(width, height)
        """
        return (self.total_width, self.total_height)

    def is_position_valid(self, x, y):
        """
        检查棋盘坐标是否有效
        
        :param x: x坐标（列）
        :param y: y坐标（行）
        :return: bool
        """
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def pixel_to_board(self, pixel_x, pixel_y):
        """
        将像素坐标转换为棋盘坐标
        
        :param pixel_x: 像素x坐标
        :param pixel_y: 像素y坐标
        :return: tuple，(board_x, board_y) 或 None（如果超出范围）
        """
        x = round((pixel_x - self.margin) / self.grid_size)
        y = round((pixel_y - self.margin) / self.grid_size)
        
        if self.is_position_valid(x, y):
            return (x, y)
        return None

    def board_to_pixel(self, board_x, board_y):
        """
        将棋盘坐标转换为像素坐标
        
        :param board_x: 棋盘x坐标
        :param board_y: 棋盘y坐标
        :return: tuple，(pixel_x, pixel_y)
        """
        pixel_x = self.margin + board_x * self.grid_size
        pixel_y = self.margin + board_y * self.grid_size
        return (pixel_x, pixel_y)

    def draw_background(self):
        """绘制背景"""
        self.screen.fill(self.background_color)

    def draw_board(self):
        """绘制棋盘网格。"""
        # 绘制背景
        self.draw_background()
        
        # 绘制网格线
        for i in range(self.board_size):
            # 水平线
            start_x = self.margin
            start_y = self.margin + i * self.grid_size
            end_x = self.margin + (self.board_size - 1) * self.grid_size
            end_y = start_y
            pygame.draw.line(self.screen, self.line_color, (start_x, start_y), (end_x, end_y), 1)

            # 垂直线
            start_x = self.margin + i * self.grid_size
            start_y = self.margin
            end_x = start_x
            end_y = self.margin + (self.board_size - 1) * self.grid_size
            pygame.draw.line(self.screen, self.line_color, (start_x, start_y), (end_x, end_y), 1)
        
        # 绘制天元等特殊点
        self._draw_special_points()

    def _draw_special_points(self):
        """绘制天元等特殊点"""
        if self.board_size == 15:
            # 标准15x15棋盘的天元和星位
            special_points = [(7, 7), (3, 3), (3, 11), (11, 3), (11, 11)]
            for x, y in special_points:
                pixel_x, pixel_y = self.board_to_pixel(x, y)
                pygame.draw.circle(self.screen, self.line_color, (pixel_x, pixel_y), 3)

    def draw_pieces(self, board_state):
        """
        根据当前棋盘状态绘制棋子。
        
        :param board_state: 二维数组, 0 表示空, 1 表示黑棋, 2 表示白棋
        """
        for y in range(self.board_size):
            for x in range(self.board_size):
                piece = board_state[y][x]
                if piece == 0:
                    continue
                
                pixel_x, pixel_y = self.board_to_pixel(x, y)
                color = self.black_piece_color if piece == 1 else self.white_piece_color
                
                # 绘制棋子
                pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), self.piece_radius)
                # 绘制棋子边框
                pygame.draw.circle(self.screen, self.piece_border_color, (pixel_x, pixel_y), self.piece_radius, 1)

    def draw_last_move_marker(self, last_move):
        """
        在最后一步棋的位置绘制标记
        
        :param last_move: tuple，(x, y) 最后一步的坐标
        """
        if last_move is None:
            return
        
        x, y = last_move
        if not self.is_position_valid(x, y):
            return
        
        pixel_x, pixel_y = self.board_to_pixel(x, y)
        # 绘制红色圆圈标记
        pygame.draw.circle(self.screen, (255, 0, 0), (pixel_x, pixel_y), self.piece_radius + 3, 2)

    def get_click_position(self, mouse_pos):
        """
        将鼠标点击位置转换为棋盘坐标。
        
        :param mouse_pos: (x_pixel, y_pixel)
        :return: (x_index, y_index) or None
        """
        return self.pixel_to_board(mouse_pos[0], mouse_pos[1])

    def draw_game_info(self, current_player, move_count, game_status=""):
        """
        绘制游戏信息
        
        :param current_player: 当前玩家编号
        :param move_count: 已下棋步数
        :param game_status: 游戏状态文本
        """
        font = pygame.font.Font(None, 24)
        info_y = 10
        
        # 当前玩家
        player_text = f"Current: {'Black' if current_player == 1 else 'White'}"
        player_surface = font.render(player_text, True, self.line_color)
        self.screen.blit(player_surface, (10, info_y))
        
        # 步数
        move_text = f"Moves: {move_count}"
        move_surface = font.render(move_text, True, self.line_color)
        self.screen.blit(move_surface, (150, info_y))
        
        # 游戏状态
        if game_status:
            status_surface = font.render(game_status, True, (255, 0, 0))
            self.screen.blit(status_surface, (10, info_y + 25))

    def highlight_position(self, x, y, color=(0, 255, 0)):
        """
        高亮显示指定位置
        
        :param x: x坐标
        :param y: y坐标
        :param color: 高亮颜色
        """
        if not self.is_position_valid(x, y):
            return
        
        pixel_x, pixel_y = self.board_to_pixel(x, y)
        pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), self.piece_radius, 3)

    def update_display(self):
        """更新显示"""
        pygame.display.flip()
