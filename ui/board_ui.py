import pygame

class BoardUI:
    def __init__(self, screen, board_size=15, grid_size=40):
        """
        初始化棋盘UI。
        :param screen: pygame 的主窗口
        :param board_size: 棋盘大小(格子数,默认15)
        :param grid_size: 每格像素大小,默认40
        """
        self.screen = screen
        self.board_size = board_size
        self.grid_size = grid_size
        self.margin = grid_size
        self.piece_radius = grid_size // 2 - 4
        self.board_pixel_size = board_size * grid_size

    def draw_board(self):
        """绘制棋盘网格。"""
        for i in range(self.board_size):
            start_x = self.margin
            start_y = self.margin + i * self.grid_size
            end_x = self.margin + (self.board_size - 1) * self.grid_size
            end_y = start_y
            pygame.draw.line(self.screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 1)

            start_x = self.margin + i * self.grid_size
            start_y = self.margin
            end_x = start_x
            end_y = self.margin + (self.board_size - 1) * self.grid_size
            pygame.draw.line(self.screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 1)

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
                center_x = self.margin + x * self.grid_size
                center_y = self.margin + y * self.grid_size
                color = (0, 0, 0) if piece == 1 else (255, 255, 255)
                pygame.draw.circle(self.screen, color, (center_x, center_y), self.piece_radius)

    def get_click_position(self, mouse_pos):
        """
        将鼠标点击位置转换为棋盘坐标。
        :param mouse_pos: (x_pixel, y_pixel)
        :return: (x_index, y_index) or None
        """
        x_pix, y_pix = mouse_pos
        x = round((x_pix - self.margin) / self.grid_size)
        y = round((y_pix - self.margin) / self.grid_size)
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            return (x, y)
        else:
            return None
