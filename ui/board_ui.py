import pygame
import os

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

        # 初始化音频
        pygame.mixer.init()
        self.background_music = None
        self.piece_sound = None

        # 按钮相关
        self.button_color = (100, 100, 100)  # 按钮颜色
        self.button_text_color = (255, 255, 255)  # 按钮文字颜色
        self.button_font = pygame.font.Font(None, 24)  # 按钮字体
        self.button_width = 100  # 按钮宽度
        self.button_height = 40  # 按钮高度
        self.button_margin = 10  # 按钮间距

        # 按钮位置
        self.undo_button_rect = None
        self.settings_button_rect = None

    def set_background_music(self, music_file):
        """
        设置并播放背景音乐。

        :param music_file: 背景音乐文件路径
        """
        self.background_music = music_file
        try:
            # 获取相对路径
            if not os.path.isabs(music_file):
                music_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), music_file)
            
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)  # 循环播放
            print("背景音乐加载成功并开始播放！")
        except Exception as e:
            print(f"背景音乐加载失败: {e}")

    def set_piece_sound(self, sound_file):
        """
        设置落子音效。

        :param sound_file: 落子音效文件路径
        """
        try:
            # 获取相对路径
            if not os.path.isabs(sound_file):
                sound_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), sound_file)
            
            self.piece_sound = pygame.mixer.Sound(sound_file)
            if self.piece_sound is None:
                print("音效加载失败，请检查文件路径和格式！")
            else:
                print("落子音效加载成功！")
        except Exception as e:
            print(f"加载音效失败: {e}")

    def play_piece_sound(self):
        """
        播放落子音效
        """
        if self.piece_sound:
            self.piece_sound.play()

    def stop_background_music(self):
        """
        停止背景音乐
        """
        pygame.mixer.music.stop()

    def pause_background_music(self):
        """
        暂停背景音乐
        """
        pygame.mixer.music.pause()

    def unpause_background_music(self):
        """
        恢复背景音乐
        """
        pygame.mixer.music.unpause()

    def set_sound_level(self, level):
        """
        设置音效音量等级
        
        :param level: 音量等级，0-100
        """
        try:
            # 设置落子音效音量
            if self.piece_sound:
                volume = level / 100.0
                self.piece_sound.set_volume(volume)
                print(f"音效音量设置为: {level}%")
        except Exception as e:
            print(f"设置音效音量失败: {e}")

    def set_background(self, background_path):
        """
        设置棋盘背景图片
        
        :param background_path: 背景图片路径
        """
        try:
            import pygame
            # 加载新背景图片
            new_background = pygame.image.load(background_path).convert()
            # 缩放到适合的尺寸（如果需要的话）
            screen_size = self.screen.get_size()
            self.background_color = None  # 使用图片背景时清除颜色背景
            self.background_image = pygame.transform.scale(new_background, screen_size)
            print(f"背景图片已更新: {background_path}")
        except Exception as e:
            print(f"设置背景图片失败: {e}")
            # 如果失败，恢复默认颜色背景
            self.background_color = (240, 217, 181)
            self.background_image = None

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
        if hasattr(self, 'background_image') and self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
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

    def draw_buttons(self):
        """
        绘制悔棋和设置按钮
        """
        # 计算按钮位置
        button_x = self.total_width + self.margin
        undo_button_y = self.margin
        settings_button_y = undo_button_y + self.button_height + self.button_margin

        # 绘制悔棋按钮
        self.undo_button_rect = pygame.Rect(button_x, undo_button_y, self.button_width, self.button_height)
        pygame.draw.rect(self.screen, self.button_color, self.undo_button_rect)
        undo_text = self.button_font.render("悔棋", True, self.button_text_color)
        self.screen.blit(undo_text, (button_x + 20, undo_button_y + 10))

        # 绘制设置按钮
        self.settings_button_rect = pygame.Rect(button_x, settings_button_y, self.button_width, self.button_height)
        pygame.draw.rect(self.screen, self.button_color, self.settings_button_rect)
        settings_text = self.button_font.render("设置", True, self.button_text_color)
        self.screen.blit(settings_text, (button_x + 20, settings_button_y + 10))

    def check_button_click(self, mouse_pos):
        """
        检测按钮点击事件

        :param mouse_pos: 鼠标点击位置
        :return: 按钮名称（"undo" 或 "settings"），如果没有点击按钮则返回 None
        """
        if self.undo_button_rect and self.undo_button_rect.collidepoint(mouse_pos):
            return "undo"
        elif self.settings_button_rect and self.settings_button_rect.collidepoint(mouse_pos):
            return "settings"
        return None