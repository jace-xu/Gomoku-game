import pygame
import os

class BoardUI:
    def __init__(self, screen, board_size=15, grid_size=40, margin=None, background_color=(255, 255, 255)):
        """
        初始化棋盘UI。
        
        :param screen: pygame 的主窗口 (必须传入，不创建新窗口)
        :param board_size: 棋盘大小(格子数,默认15)
        :param grid_size: 每格像素大小,默认40
        :param margin: 边距，如果为None则等于grid_size
        :param background_color: 背景颜色
        """
        if screen is None:
            raise ValueError("screen参数不能为None，必须传入已存在的pygame display surface")
        
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

        # 背景图片相关 - 新增属性
        self.background_image = None  # 背景图片Surface对象
        self.use_background_image = False  # 是否使用背景图片

        # 初始化音频
        pygame.mixer.init()
        self.background_music = None
        self.piece_sound = None
        self.current_bgm_volume = 0.5  # 当前BGM音量（0.0-1.0）

        # 按钮相关
        self.button_color = (100, 100, 100)  # 按钮颜色
        self.button_text_color = (255, 255, 255)  # 按钮文字颜色
        self._init_button_font()  # 使用统一的字体初始化
        self.button_width = 100  # 按钮宽度
        self.button_height = 40  # 按钮高度
        self.button_margin = 10  # 按钮间距

        # 按钮位置
        self.undo_button_rect = None
        self.settings_button_rect = None

        # 自动加载默认音频
        self._load_default_audio()

    def _init_button_font(self):
        """初始化按钮字体，使用项目中的Calibri字体"""
        # 定义字体路径（相对路径）- 使用Calibri系列字体
        font_paths = [
            "assets/calibrib.ttf",   # Calibri Bold
            "assets/calibri.ttf",    # Calibri Regular
            "assets/calibril.ttf",   # Calibri Light
            "assets/calibriz.ttf",   # Calibri Light Italic
            "assets/calibrii.ttf",   # Calibri Italic
            "assets/calibrili.ttf"   # Calibri Light Italic
        ]
        
        # 尝试加载字体
        for font_path in font_paths:
            try:
                self.button_font = pygame.font.Font(font_path, 24)
                print(f"成功加载字体: {font_path}")
                return
            except (OSError, pygame.error):
                continue
        
        # 如果所有字体都加载失败，使用默认字体
        self.button_font = pygame.font.Font(None, 24)
        print("所有字体加载失败，使用默认字体")

    def _load_default_audio(self):
        """加载默认音频文件"""
        try:
            # 加载默认BGM
            default_bgm_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "BGM", "board_bgm.mp3")
            if os.path.exists(default_bgm_path):
                self.set_background_music("assets/BGM/board_bgm.mp3")
            else:
                print(f"默认BGM文件不存在: {default_bgm_path}")
            
            # 加载默认落子音效
            default_sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "piece_sound.mp3")
            if os.path.exists(default_sound_path):
                self.set_piece_sound("assets/piece_sound.mp3")
            else:
                print(f"默认音效文件不存在: {default_sound_path}")
        except Exception as e:
            print(f"加载默认音频失败: {e}")

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
            
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)  # 循环播放
                pygame.mixer.music.set_volume(self.current_bgm_volume)
                print(f"背景音乐加载成功并开始播放: {music_file}")
            else:
                print(f"背景音乐文件不存在: {music_file}")
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
            
            if os.path.exists(sound_file):
                self.piece_sound = pygame.mixer.Sound(sound_file)
                if self.piece_sound is None:
                    print("音效加载失败，请检查文件路径和格式！")
                else:
                    print("落子音效加载成功！")
            else:
                print(f"音效文件不存在: {sound_file}")
        except Exception as e:
            print(f"加载音效失败: {e}")

    def set_bgm_file(self, bgm_file):
        """
        设置BGM文件但不立即播放（用于设置界面）
        
        :param bgm_file: BGM文件名（相对于BGM文件夹）
        """
        if bgm_file is None:
            # 停止音乐
            pygame.mixer.music.stop()
            self.background_music = None
            print("BGM已停止")
        else:
            # 构建完整路径
            bgm_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "BGM", bgm_file)
            if os.path.exists(bgm_path):
                try:
                    pygame.mixer.music.load(bgm_path)
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(self.current_bgm_volume)
                    self.background_music = bgm_path
                    print(f"BGM已切换到: {bgm_file}")
                except Exception as e:
                    print(f"BGM切换失败: {e}")
            else:
                print(f"BGM文件不存在: {bgm_path}")

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
            
            # 设置BGM音量
            self.current_bgm_volume = level / 100.0
            pygame.mixer.music.set_volume(self.current_bgm_volume)
            
            print(f"音量设置为: {level}%")
        except Exception as e:
            print(f"设置音量失败: {e}")

    def set_background(self, background_path):
        """
        设置棋盘背景图片
        
        :param background_path: 背景图片路径
        """
        try:
            print(f"尝试加载背景: {background_path}")
            # 加载新背景图片
            new_background = pygame.image.load(background_path).convert()
            # 缩放到适合的尺寸
            screen_size = self.screen.get_size()
            self.background_image = pygame.transform.scale(new_background, screen_size)
            self.use_background_image = True  # 启用背景图片
            print(f"背景图片已更新并启用: {background_path}")
            print(f"背景图片尺寸: {self.background_image.get_size()}")
            print(f"屏幕尺寸: {screen_size}")
        except Exception as e:
            print(f"设置背景图片失败: {e}")
            # 如果失败，恢复使用颜色背景
            self.use_background_image = False
            self.background_image = None

    def draw_background(self):
        """绘制背景"""
        if self.use_background_image and self.background_image:
            # 使用背景图片
            self.screen.blit(self.background_image, (0, 0))
        else:
            # 使用背景颜色
            self.screen.fill(self.background_color)

    def draw_board(self):
        """绘制棋盘网格。"""
        # 绘制网格线，不要清除背景
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

    def board_to_pixel(self, board_x, board_y):
        """
        将棋盘坐标转换为像素坐标
        
        :param board_x: 棋盘x坐标（列）
        :param board_y: 棋盘y坐标（行）
        :return: (pixel_x, pixel_y) 像素坐标
        """
        pixel_x = self.margin + board_x * self.grid_size
        pixel_y = self.margin + board_y * self.grid_size
        return pixel_x, pixel_y

    def pixel_to_board(self, pixel_x, pixel_y):
        """
        将像素坐标转换为棋盘坐标
        
        :param pixel_x: 像素x坐标
        :param pixel_y: 像素y坐标
        :return: (board_x, board_y) 棋盘坐标，如果超出范围则返回None
        """
        # 检查是否在棋盘区域内
        if (pixel_x < self.margin or pixel_x > self.margin + (self.board_size - 1) * self.grid_size or
            pixel_y < self.margin or pixel_y > self.margin + (self.board_size - 1) * self.grid_size):
            return None
        
        # 计算棋盘坐标
        board_x = round((pixel_x - self.margin) / self.grid_size)
        board_y = round((pixel_y - self.margin) / self.grid_size)
        
        # 确保坐标在有效范围内
        if 0 <= board_x < self.board_size and 0 <= board_y < self.board_size:
            return board_x, board_y
        else:
            return None

    def is_position_valid(self, x, y):
        """
        检查位置是否有效
        
        :param x: x坐标
        :param y: y坐标
        :return: bool，位置是否有效
        """
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def play_piece_sound(self):
        """播放落子音效"""
        try:
            if self.piece_sound:
                self.piece_sound.play()
        except Exception as e:
            print(f"播放落子音效失败: {e}")

    def clear_screen(self):
        """完全清除屏幕内容"""
        self.screen.fill(self.background_color)