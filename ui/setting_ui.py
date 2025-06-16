import pygame
import os
import random
import traceback

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BEIGE = (245, 245, 220)
BLUE = (80, 150, 255)
YELLOW = (255, 220, 80)

class SettingUI:
    """
    游戏设置界面UI类，负责处理设置窗口的显示、事件处理与设置参数的调整。
    包括难度、音量、背景、BGM等设置。
    """

    def __init__(self, screen, move_logic, board_ui, assets_path="assets", background_image="assets/loadbackground.jpg"):
        """
        初始化SettingUI类。
        :param screen: pygame的主窗口Surface对象
        :param move_logic: 游戏逻辑对象（如AI难度设置等）
        :param board_ui: 棋盘UI对象（如设置背景、音效等）
        :param assets_path: 资源文件夹路径
        :param background_image: 默认背景图片路径
        """
        self.screen = screen  # 游戏主窗口
        self.move_logic = move_logic  # 移动/AI逻辑对象
        self.board_ui = board_ui  # 棋盘UI对象
        self.assets_path = assets_path  # 资源目录路径
        self.background_image_path = background_image  # 背景图片路径

        try:
            self.font = pygame.font.Font("msyh.ttf", 36)  # 普通字体
            self.title_font = pygame.font.Font("msyh.ttf", 48)  # 标题字体
            self.button_font = pygame.font.Font("msyh.ttf", 28)  # 按钮字体
        except (OSError, pygame.error):
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 28)

        self.background = None  # 背景图片Surface对象
        self._load_background_image()  # 加载背景图片

        self.difficulty_levels = ["Easy", "Normal", "Hard"]  # 难度选项
        self.difficulty_map = {"Easy": 1, "Normal": 2, "Hard": 3}  # 难度等级映射
        self.selected_difficulty = "Normal"  # 当前选择的难度
        self.sound_level = 50  # 音量等级，范围0-100

        self.background_list = self._load_backgrounds()  # 背景图片文件名列表
        self.selected_background = self.background_list[0] if self.background_list else None  # 当前选中背景
        self.background_thumbnails = {}  # 背景缩略图字典，key为文件名，value为Surface
        for bg in self.background_list:
            try:
                bg_path = os.path.join(self.assets_path, "backgrounds", bg)
                image = pygame.image.load(bg_path).convert()
                thumb = pygame.transform.smoothscale(image, (160, 120))
                self.background_thumbnails[bg] = thumb
            except (OSError, pygame.error) as e:
                print(f"Failed to load background {bg}: {e}")
                self.background_thumbnails[bg] = None
        self.bg_scroll_index = 0  # 背景分页起始索引
        self.bg_per_page = 4  # 每页显示背景数量
        self.bg_preview = None  # 预览大图Surface
        self.bg_preview_name = None  # 预览大图文件名
        self.bg_preview_rect = None  # 预览大图位置Rect
        self.bg_select_buttons = []  # 背景选择按钮的Rect列表

        # === BGM相关 ===
        self.bgm_path = os.path.join(self.assets_path, "BGM")  # BGM资源目录
        self.bgm_list = self._load_bgms()  # BGM文件名列表
        self.bgm_list_display = [None] + self.bgm_list  # BGM显示列表（None表示静音）
        if self.bgm_list:
            self.selected_bgm = random.choice(self.bgm_list)  # 随机初始BGM
        else:
            self.selected_bgm = None
        try:
            pygame.mixer.init()
            self._play_bgm(self.selected_bgm)
            self._set_bgm_volume(self.sound_level)
        except Exception as e:
            print("BGM初始化或播放异常:", e)
            traceback.print_exc()

        self.state = "main"  # 当前界面状态
        self.running = False  # 控制定时循环标志

    def _load_background_image(self):
        """
        加载主背景图片到self.background。
        如果加载失败，则置为None并输出错误信息。
        """
        try:
            self.background = pygame.image.load(self.background_image_path).convert()
            self.background = pygame.transform.scale(self.background, self.screen.get_size())
        except (OSError, pygame.error) as e:
            print(f"加载背景图片失败: {e}")
            self.background = None

    def _load_backgrounds(self):
        """
        加载背景图片文件夹下的所有背景文件名。
        :return: 背景文件名列表
        """
        bg_dir = os.path.join(self.assets_path, "backgrounds")
        if not os.path.exists(bg_dir):
            return []
        return [f for f in os.listdir(bg_dir) if f.lower().endswith(('.png', '.jpg', '.bmp'))]

    def _load_bgms(self):
        """
        加载BGM文件夹下所有mp3文件名。
        :return: BGM文件名列表
        """
        if not os.path.exists(self.bgm_path):
            return []
        return [f for f in os.listdir(self.bgm_path) if f.lower().endswith(".mp3")]

    def _play_bgm(self, bgm_name):
        """
        播放指定BGM文件，或静音（bgm_name为None）。
        :param bgm_name: BGM文件名或None
        """
        try:
            if hasattr(self.board_ui, 'set_bgm_file'):
                # 如果board_ui有set_bgm_file方法，使用它
                self.board_ui.set_bgm_file(bgm_name)
            else:
                # 否则使用原来的方法
                if bgm_name is None:
                    pygame.mixer.music.stop()
                else:
                    bgm_file_path = os.path.join(self.bgm_path, bgm_name)
                    try:
                        pygame.mixer.music.load(bgm_file_path)
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(self.sound_level / 100.0)
                    except (OSError, pygame.error) as e:
                        print(f"BGM加载失败: {e}")
        except Exception as e:
            print(f"播放BGM异常: {e}")

    @staticmethod
    def _set_bgm_volume(level):
        """
        设置BGM音量（0-100）。
        :param level: 音量等级，0-100
        """
        try:
            pygame.mixer.music.set_volume(level / 100.0)
        except Exception as e:
            print("设置BGM音量异常:", e)
            traceback.print_exc()

    def show(self):
        """
        显示设置窗口主循环。
        根据当前state绘制界面并处理事件。
        """
        self.running = True
        clock = pygame.time.Clock()
        while self.running:
            try:
                if self.background:
                    self.screen.blit(self.background, (0, 0))
                else:
                    self.screen.fill(WHITE)
                self.handle_event()
                if self.state == "main":
                    self.draw_main()
                elif self.state == "difficulty":
                    self.draw_difficulty()
                elif self.state == "sound":
                    self.draw_sound()
                elif self.state == "background":
                    self.draw_background()
                pygame.display.flip()
                clock.tick(60)
            except Exception as e:
                print("[UI] 主循环异常:", e)
                traceback.print_exc()

    def handle_event(self):
        """
        事件处理函数，包括鼠标点击、滚轮、键盘等。
        根据当前state分发事件逻辑。
        """
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # 背景界面事件
                    if self.state == "background":
                        if self.bg_preview:
                            self.bg_preview = None
                            self.bg_preview_name = None
                            return
                        total = len(self.background_list)
                        start = self.bg_scroll_index
                        end = min(start + self.bg_per_page, total)
                        thumb_w, thumb_h = 160, 120
                        gap = 20
                        count = end - start
                        group_width = count * thumb_w + (count-1)*gap
                        start_x = (self.screen.get_width() - group_width) // 2

                        if event.button == 1:
                            # 上一页
                            if start > 0 and 120 <= mx <= 140 and 220 <= my <= 260:
                                self.bg_scroll_index = max(0, start - self.bg_per_page)
                                return
                            # 下一页
                            if end < total and 840 <= mx <= 860 and 220 <= my <= 260:
                                self.bg_scroll_index = min(total - self.bg_per_page, start + self.bg_per_page)
                                return
                            # 点击缩略图预览
                            for i, idx in enumerate(range(start, end)):
                                rect = pygame.Rect(start_x + i*(thumb_w+gap), 180, thumb_w, thumb_h)
                                if rect.collidepoint(mx, my):
                                    bg = self.background_list[idx]
                                    bg_path = os.path.join(self.assets_path, "backgrounds", bg)
                                    try:
                                        img = pygame.image.load(bg_path).convert()
                                        self.bg_preview = img
                                        self.bg_preview_name = bg
                                    except (OSError, pygame.error):
                                        self.bg_preview = None
                                    return
                            # 选择背景按钮
                            for i, btn_rect in enumerate(self.bg_select_buttons):
                                if btn_rect.collidepoint(mx, my):
                                    bg = self.background_list[start + i]
                                    self.selected_background = bg
                                    self.update_background(bg)
                                    return
                            # 返回按钮
                            if self._in_rect(mx, my, 20, 520, 120, 50):
                                self.state = "main"
                    # 主菜单事件
                    elif self.state == "main":
                        center_x = (self.screen.get_width() - 300) // 2
                        if self._in_rect(mx, my, center_x, 200, 300, 60):
                            self.state = "difficulty"
                        elif self._in_rect(mx, my, center_x, 300, 300, 60):
                            self.state = "sound"
                        elif self._in_rect(mx, my, center_x, 400, 300, 60):
                            self.state = "background"
                        elif self._in_rect(mx, my, 20, 520, 120, 50):
                            self.running = False
                    # 难度设置事件
                    elif self.state == "difficulty":
                        center_x = (self.screen.get_width() - 260) // 2
                        for i, level in enumerate(self.difficulty_levels):
                            if self._in_rect(mx, my, center_x, 200 + i*80, 260, 60):
                                self.selected_difficulty = level
                                self.update_difficulty(level)
                        if self._in_rect(mx, my, 20, 520, 120, 50):
                            self.state = "main"
                    # 音量BGM设置事件
                    elif self.state == "sound":
                        bar_width = 400
                        bar_x = (self.screen.get_width() - bar_width) // 2
                        # 音量条
                        if bar_x <= mx <= bar_x + bar_width and 250 <= my <= 290:
                            self.sound_level = int((mx - bar_x) / bar_width * 100)
                            self.update_sound(self.sound_level)
                        # BGM选择
                        if self.bgm_list_display:
                            start_y = 380
                            for i, bgm in enumerate(self.bgm_list_display):
                                btn_x = (self.screen.get_width()-180)//2
                                btn_y = start_y + i*50
                                if self._in_rect(mx, my, btn_x, btn_y, 180, 40):
                                    if self.selected_bgm != bgm:
                                        self.selected_bgm = bgm
                                        self._play_bgm(bgm)
                                        # 确保音量设置正确
                                        self._set_bgm_volume(self.sound_level)
                                    break
                        # 返回按钮
                        if self._in_rect(mx, my, 20, 520, 120, 50):
                            self.state = "main"
                # 鼠标滚轮翻页
                elif event.type == pygame.MOUSEWHEEL and self.state == "background" and not self.bg_preview:
                    total = len(self.background_list)
                    if event.y > 0:
                        self.bg_scroll_index = max(0, self.bg_scroll_index - self.bg_per_page)
                    elif event.y < 0:
                        self.bg_scroll_index = min(max(0, total - self.bg_per_page), self.bg_scroll_index + self.bg_per_page)
                # 预览时esc关闭
                elif event.type == pygame.KEYDOWN:
                    if self.bg_preview and event.key == pygame.K_ESCAPE:
                        self.bg_preview = None
                        self.bg_preview_name = None
        except Exception as e:
            print("[UI] 事件处理异常:", e)
            traceback.print_exc()

    def draw_main(self):
        """
        绘制主设置菜单，包括“难度”、“音量”、“背景”、“返回”四个按钮。
        """
        self._draw_title("Settings")
        center_x = (self.screen.get_width() - 300) // 2
        self._draw_button("Difficulty", center_x, 200, 300, 60)
        self._draw_button("Sound", center_x, 300, 300, 60)
        self._draw_button("Background", center_x, 400, 300, 60)
        self._draw_button("Back", 20, 520, 120, 50, color=GRAY)

    def draw_difficulty(self):
        """
        绘制难度设置界面，包括难度选项按钮和返回按钮。
        """
        self._draw_title("Difficulty")
        center_x = (self.screen.get_width() - 260) // 2
        for i, level in enumerate(self.difficulty_levels):
            color = (245, 245, 220) if self.selected_difficulty == level else GRAY
            self._draw_button(level, center_x, 200 + i*80, 260, 60, color=color)
        self._draw_button("Back", 20, 520, 120, 50, color=GRAY)

    def draw_sound(self):
        """
        绘制音量与BGM设置界面，包括音量条、BGM列表与返回按钮。
        """
        self._draw_title("Sound")
        # 音量条
        bar_width = 400
        bar_x = (self.screen.get_width() - bar_width) // 2
        pygame.draw.rect(self.screen, GRAY, (bar_x, 250, bar_width, 40), border_radius=10)
        pygame.draw.rect(self.screen, (80, 180, 80), (bar_x, 250, int(self.sound_level*bar_width/100), 40), border_radius=10)
        handle_x = bar_x + int(self.sound_level*bar_width/100)
        pygame.draw.circle(self.screen, BEIGE, (handle_x, 270), 22)
        pygame.draw.circle(self.screen, BLACK, (handle_x, 270), 22, 2)
        txt = self.font.render(f"Volume: {self.sound_level}", True, BLACK)
        self.screen.blit(txt, ((self.screen.get_width()-txt.get_width())//2, 200))

        # BGM列表
        if self.bgm_list_display:
            start_y = 380
            title_txt = self.font.render("BGM:", True, BLACK)
            self.screen.blit(title_txt, ((self.screen.get_width()-title_txt.get_width())//2, start_y-40))
            for i, bgm in enumerate(self.bgm_list_display):
                label = "No BGM" if bgm is None else bgm[:-4]
                color = BEIGE if self.selected_bgm == bgm else GRAY
                btn_x = (self.screen.get_width()-180)//2
                btn_y = start_y + i*50
                self._draw_button(label, btn_x, btn_y, 180, 40, color=color)
        else:
            empty_txt = self.font.render("No BGM found.", True, BLACK)
            self.screen.blit(empty_txt, ((self.screen.get_width()-empty_txt.get_width())//2, 400))
        self._draw_button("Back", 20, 520, 120, 50, color=GRAY)

    def draw_background(self):
        """
        绘制背景选择界面，包括背景缩略图列表、选择按钮、分页箭头、返回按钮及大图预览。
        """
        self._draw_title("Background")
        total = len(self.background_list)
        start = self.bg_scroll_index
        end = min(start + self.bg_per_page, total)
        thumb_w, thumb_h = 160, 120
        gap = 20
        btn_w, btn_h = 100, 36
        count = end - start
        group_width = count * thumb_w + (count-1)*gap if count>0 else 0
        start_x = (self.screen.get_width() - group_width) // 2 if count>0 else 0
        self.bg_select_buttons = []
        for i, idx in enumerate(range(start, end)):
            bg = self.background_list[idx]
            rect = pygame.Rect(start_x + i*(thumb_w+gap), 180, thumb_w, thumb_h)
            if self.selected_background == bg:
                pygame.draw.rect(self.screen, BLUE, rect, 6, border_radius=18)
                highlight = pygame.Surface((thumb_w, thumb_h), pygame.SRCALPHA)
                highlight.fill((YELLOW[0], YELLOW[1], YELLOW[2], 80))
                self.screen.blit(highlight, rect.topleft)
            pygame.draw.rect(self.screen, BEIGE, rect, border_radius=12)
            pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=12)
            thumb = self.background_thumbnails.get(bg)
            if thumb:
                self.screen.blit(thumb, (rect.x, rect.y))
            else:
                pygame.draw.rect(self.screen, GRAY, rect)
            btn_x = rect.x + (thumb_w - btn_w)//2
            btn_y = rect.y + thumb_h + 10
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.bg_select_buttons.append(btn_rect)
            btn_color = (245, 245, 220) if self.selected_background == bg else GRAY
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2, border_radius=8)
            label = "chosen" if self.selected_background == bg else "choose"
            txt_btn = self.button_font.render(label, True, BLACK)
            self.screen.blit(txt_btn, (btn_x + (btn_w-txt_btn.get_width())//2, btn_y + (btn_h-txt_btn.get_height())//2))
        # 分页箭头
        if start > 0:
            pygame.draw.polygon(self.screen, BLACK, [(start_x-20,240),(start_x,220),(start_x,260)])
        if end < total:
            right_x = start_x + count*thumb_w + (count-1)*gap
            pygame.draw.polygon(self.screen, BLACK, [(right_x+20,240),(right_x,220),(right_x,260)])
        self._draw_button("Back", 20, 520, 120, 50, color=GRAY)
        # 预览大图
        if self.bg_preview:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            img = self.bg_preview
            w, h = img.get_width(), img.get_height()
            maxw, maxh = 600, 400
            scale = min(maxw/w, maxh/h, 1.0)
            img2 = pygame.transform.smoothscale(img, (int(w*scale), int(h*scale)))
            rect = img2.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(img2, rect.topleft)
            self.bg_preview_rect = rect
            name_txt = self.font.render(self.bg_preview_name, True, WHITE)
            self.screen.blit(name_txt, (rect.x+10, rect.y+10))

    def update_difficulty(self, level):
        """
        更新难度设置并同步到move_logic对象。
        :param level: 难度字符串，例如 "Easy"
        """
        try:
            difficulty_value = self.difficulty_map[level]
            # 尝试多种可能的方法名
            if hasattr(self.move_logic, "set_difficulty_level"):
                self.move_logic.set_difficulty_level(difficulty_value)
            elif hasattr(self.move_logic, "set_difficulty"):
                self.move_logic.set_difficulty(difficulty_value)
            elif hasattr(self.move_logic, "SEARCH_DEPTH"):
                setattr(self.move_logic, "SEARCH_DEPTH", difficulty_value)
            elif hasattr(self.move_logic, "difficulty"):
                setattr(self.move_logic, "difficulty", difficulty_value)
            else:
                print(f"AI对象不支持难度设置，尝试设置搜索深度")
                # 直接设置可能存在的属性
                for attr_name in ["search_depth", "depth", "level"]:
                    if hasattr(self.move_logic, attr_name):
                        setattr(self.move_logic, attr_name, difficulty_value)
                        print(f"已设置 {attr_name} = {difficulty_value}")
                        break
            print(f"AI难度已设置为: {level} (值: {difficulty_value})")
        except Exception as e:
            print("设置难度异常:", e)
            traceback.print_exc()

    def update_sound(self, level):
        """
        更新音量设置并同步到board_ui和BGM音量。
        :param level: 音量，0-100
        """
        try:
            if hasattr(self.board_ui, "set_sound_level"):
                self.board_ui.set_sound_level(level)
            else:
                # 如果board_ui没有set_sound_level方法，直接设置pygame音量
                pygame.mixer.music.set_volume(level / 100.0)
                if hasattr(self.board_ui, 'piece_sound') and self.board_ui.piece_sound:
                    self.board_ui.piece_sound.set_volume(level / 100.0)
            self._set_bgm_volume(level)
        except Exception as e:
            print("设置音量异常:", e)
            traceback.print_exc()

    def update_background(self, bg_name):
        """
        更新背景图片并同步到board_ui。
        :param bg_name: 背景文件名
        """
        try:
            if hasattr(self.board_ui, "set_background"):
                bg_path = os.path.join(self.assets_path, "backgrounds", bg_name)
                self.board_ui.set_background(bg_path)
        except Exception as e:
            print("设置背景异常:", e)
            traceback.print_exc()

    def get_settings(self):
        """
        获取当前设置参数字典。
        :return: dict，包括难度、音量、背景、BGM
        """
        return {
            "difficulty": self.selected_difficulty,
            "sound": self.sound_level,
            "background": self.selected_background,
            "bgm": self.selected_bgm
        }

    def set_settings(self, settings):
        """
        设置参数并同步到相关对象。
        :param settings: dict，包括difficulty, sound, background, bgm等
        """
        try:
            if "difficulty" in settings:
                self.selected_difficulty = settings["difficulty"]
                self.update_difficulty(settings["difficulty"])
            if "sound" in settings:
                self.sound_level = settings["sound"]
                self.update_sound(settings["sound"])
            if "background" in settings and settings["background"] in self.background_list:
                self.selected_background = settings["background"]
                self.update_background(settings["background"])
            if "bgm" in settings and settings["bgm"] in self.bgm_list_display:
                self.selected_bgm = settings["bgm"]
                self._play_bgm(settings["bgm"])
                self._set_bgm_volume(self.sound_level)
            elif "bgm" in settings and settings["bgm"] is None:
                self.selected_bgm = None
                self._play_bgm(None)
        except Exception as e:
            print("设置参数异常:", e)
            traceback.print_exc()

    def _draw_title(self, text):
        """
        居中绘制标题文本。
        :param text: 标题内容
        """
        txt = self.title_font.render(text, True, BLACK)
        self.screen.blit(txt, (self.screen.get_width()//2 - txt.get_width()//2, 90))

    def _draw_button(self, text, x, y, w, h, color=BEIGE):
        """
        绘制按钮。
        :param text: 按钮文本
        :param x: x坐标
        :param y: y坐标
        :param w: 按钮宽度
        :param h: 按钮高度
        :param color: 按钮背景色
        """
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=12)
        txt = self.font.render(text, True, BLACK)
        self.screen.blit(txt, (x + (w - txt.get_width())//2, y + (h - txt.get_height())//2))

    @staticmethod
    def _in_rect(mx, my, x, y, w, h):
        """
        判断点(mx, my)是否在矩形(x, y, w, h)内。
        :param mx: 鼠标x坐标
        :param my: 鼠标y坐标
        :param x: 矩形左上x
        :param y: 矩形左上y
        :param w: 宽度
        :param h: 高度
        :return: True/False
        """
        return x <= mx <= x + w and y <= my <= y + h