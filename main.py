import pygame
import sys
import os
import json
from datetime import datetime

# 导入自定义模块
from logic.board_state import BoardState  # 棋盘状态管理模块，负责棋盘逻辑和游戏规则
from logic.move_logic import GomokuAI     # AI决策模块，负责AI下棋策略
from logic.comment import GameCommentator # AI评语生成模块
from ui.menu_ui import GameUI             # 游戏UI管理模块，负责菜单显示
from ui.board_ui import BoardUI           # 棋盘UI模块，负责棋盘绘制和交互
from ui.past_ui import HistoryUI          # 历史记录UI模块
from ui.setting_ui import SettingUI       # 设置UI模块

# 导入动画模块
from ui.animation_ui import create_animation_player
# 导入模式选择模块
from ui.mode_selection_ui import ModeSelectionUI

class GomokuGame:
    """五子棋游戏主类 - 整合所有模块，管理游戏流程"""
    
    def __init__(self, board_size=15, screen_width=800, screen_height=600):
        """
        初始化游戏实例
        
        :param board_size: 棋盘大小（15表示15x15棋盘）
        :param screen_width: 游戏窗口初始宽度
        :param screen_height: 游戏窗口初始高度
        """
        # 游戏配置参数
        self.board_size = board_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 玩家配置 - 定义黑白棋执子方
        self.human_player = 1  # 人类玩家执黑棋（按照五子棋规则黑棋先手）
        self.ai_player = 2     # AI玩家执白棋
        
        # 初始化pygame游戏引擎
        pygame.init()
        self.screen = None  # 游戏屏幕对象，在_init_game_screen中初始化
        self.clock = pygame.time.Clock()  # 游戏时钟，用于控制帧率
        
        # 初始化游戏核心组件
        self.board_state = None  # 棋盘状态管理器
        self.ai = None          # AI决策器
        self.board_ui = None    # 棋盘UI渲染器
        self.game_ui = None     # 游戏UI管理器
        
        # 游戏运行状态控制
        self.running = True      # 主程序是否运行
        self.game_active = False # 当前是否在游戏中（区别于在菜单中）
        
        # 初始化评语生成器
        self.commentator = GameCommentator()
        
        # 设置UI实例
        self.setting_ui = None
        
        # 背景设置持久化
        self.current_background = None  # 当前选中的背景文件路径
        self.current_difficulty = 'Normal'  # 默认难度
        self._load_settings()  # 加载保存的设置
        
        # 动画播放器
        self.animation_player = None
        
        # 游戏模式相关
        self.game_mode = "vs_ai"  # 默认为AI对战模式 ("vs_ai" 或 "vs_human")
        self.mode_selection_ui = None
        
        # 调用初始化方法
        self._init_game_components()
    
    def _load_settings(self):
        """加载保存的游戏设置"""
        try:
            settings_file = os.path.join(os.path.dirname(__file__), 'game_database', 'settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_background = settings.get('background_path', None)
                    self.current_difficulty = settings.get('difficulty', 'Normal')
                    print(f"加载设置 - 背景: {self.current_background}, 难度: {self.current_difficulty}")
        except Exception as e:
            print(f"加载设置失败: {e}")
            self.current_background = None
            self.current_difficulty = 'Normal'

    def _save_settings(self):
        """保存游戏设置"""
        try:
            settings_dir = os.path.join(os.path.dirname(__file__), 'game_database')
            os.makedirs(settings_dir, exist_ok=True)
            settings_file = os.path.join(settings_dir, 'settings.json')
            
            settings = {
                'background_path': self.current_background,
                'difficulty': getattr(self, 'current_difficulty', 'Normal')
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            print(f"设置已保存 - 背景: {self.current_background}, 难度: {getattr(self, 'current_difficulty', 'Normal')}")
        except Exception as e:
            print(f"保存设置失败: {e}")

    def update_difficulty_setting(self, difficulty):
        """更新难度设置并持久化"""
        print(f"游戏实例更新难度设置: {difficulty}")
        self.current_difficulty = difficulty
        
        # 立即应用到AI
        if self.ai:
            difficulty_map = {"Easy": 1, "Normal": 2, "Hard": 3}
            if difficulty in difficulty_map:
                difficulty_level = difficulty_map[difficulty]
                success = self.ai.set_difficulty_level(difficulty_level)
                if success:
                    print(f"AI难度立即更新成功: {difficulty} (级别: {difficulty_level})")
                else:
                    print(f"AI难度立即更新失败: {difficulty}")
        
        # 保存到文件
        self._save_settings()
        print(f"难度设置已更新并保存: {difficulty}")

    def update_background_setting(self, background_path):
        """更新背景设置并持久化"""
        self.current_background = background_path
        self._save_settings()
        # 如果board_ui已初始化，立即应用背景
        if self.board_ui:
            self.board_ui.set_background(background_path)

    def _init_game_components(self):
        """初始化游戏核心组件 - 创建各个模块的实例"""
        
        # 初始化GameUI：负责开始菜单和结果显示的UI管理器
        # GameUI.show_start_menu() - 显示开始菜单
        # GameUI.show_result_menu() - 显示游戏结果
        self.game_ui = GameUI(self.screen_width, self.screen_height)
        
        # 初始化BoardState：棋盘状态和游戏规则管理
        # 参数说明：size=棋盘大小，ai_player=AI执子颜色，human_player=人类执子颜色，first_player=先手方
        self.board_state = BoardState(
            size=self.board_size,
            ai_player=self.ai_player,
            human_player=self.human_player,
            first_player=self.human_player  # 人类先手（黑棋先手是五子棋标准规则）
        )
        
        # 初始化GomokuAI：AI决策和棋力计算模块
        # 参数说明：board_size=棋盘大小，ai_player=AI执子颜色，human_player=人类执子颜色
        self.ai = GomokuAI(
            board_size=self.board_size,
            ai_player=self.ai_player,
            human_player=self.human_player
        )
        
        # 应用保存的难度设置
        if hasattr(self, 'current_difficulty'):
            difficulty_map = {"Easy": 1, "Normal": 2, "Hard": 3}
            if self.current_difficulty in difficulty_map:
                difficulty_level = difficulty_map[self.current_difficulty]
                success = self.ai.set_difficulty_level(difficulty_level)
                if success:
                    print(f"应用保存的难度设置成功: {self.current_difficulty} (级别: {difficulty_level})")
                else:
                    print(f"应用保存的难度设置失败: {self.current_difficulty}")

    def _init_game_screen(self):
        """初始化游戏屏幕和棋盘UI - 根据棋盘大小计算合适的显示尺寸"""
        
        # 计算合适的网格大小：根据屏幕尺寸和棋盘大小自动调整
        # 确保棋盘能完整显示在屏幕上，同时保持合理的视觉效果
        grid_size = min(
            (self.screen_width - 100) // self.board_size,   # 基于宽度计算
            (self.screen_height - 100) // self.board_size   # 基于高度计算
        )
        grid_size = max(25, min(40, grid_size))  # 限制网格大小在25-40像素之间，保证可用性
        
        # 根据计算出的网格大小重新计算实际需要的屏幕尺寸
        margin = 50  # 棋盘边距
        required_width = self.board_size * grid_size + 2 * margin
        required_height = self.board_size * grid_size + 2 * margin + 100  # 额外100像素用于显示游戏信息
        
        # pygame.display.set_mode() - 创建游戏窗口
        self.screen = pygame.display.set_mode((required_width, required_height))
        pygame.display.set_caption("Gomoku Game")  # 设置窗口标题
        
        # 初始化BoardUI：棋盘绘制和交互处理模块
        # 参数说明：screen=绘制目标，board_size=棋盘大小，grid_size=网格像素大小，margin=边距，background_color=背景色
        self.board_ui = BoardUI(
            screen=self.screen,
            board_size=self.board_size,
            grid_size=grid_size,
            margin=margin,
            background_color=(240, 217, 181)  # 木制棋盘的暖色调
        )
        
        # 应用保存的背景设置
        if self.current_background and os.path.exists(self.current_background):
            self.board_ui.set_background(self.current_background)
        else:
            # 如果没有保存的背景或背景文件不存在，使用默认背景
            self.board_ui.set_background(None)
        
        # 初始化音频
        self._init_audio()
        
        # 初始化设置UI
        self._init_setting_ui()
        
        # 初始化动画播放器
        self._init_animation_player()
        
        # 初始化模式选择UI
        self._init_mode_selection_ui()

    def _init_audio(self):
        """初始化游戏音频"""
        try:
            # 设置背景音乐和落子音效（使用相对路径）
            self.board_ui.set_background_music("assets/BGM/board_bgm.mp3")
            self.board_ui.set_piece_sound("assets/piece_sound.mp3")
        except Exception as e:
            print(f"音频初始化失败: {e}")

    def _init_setting_ui(self):
        """初始化设置UI"""
        if self.screen and self.ai and self.board_ui:
            self.setting_ui = SettingUI(
                screen=self.screen,
                move_logic=self.ai,
                board_ui=self.board_ui,
                assets_path="assets",
                background_image="assets/loadbackground.jpg",
                game_instance=self  # 传递游戏实例引用
            )

    def _init_animation_player(self):
        """初始化动画播放器"""
        if self.screen:
            self.animation_player = create_animation_player(self.screen)

    def _init_mode_selection_ui(self):
        """初始化模式选择UI"""
        if self.screen:
            self.mode_selection_ui = ModeSelectionUI(
                screen_width=self.screen.get_width(),
                screen_height=self.screen.get_height(),
                screen=self.screen
            )

    def start_game(self):
        """开始新游戏 - 重置所有游戏状态"""
        
        # BoardState.reset() - 重置棋盘状态到初始状态
        # 参数：first_player指定先手玩家
        self.board_state.reset(first_player=self.human_player)
        
        # GomokuAI.reset_board() - 重置AI的内部棋盘状态
        self.ai.reset_board()
        
        # 设置游戏为活跃状态
        self.game_active = True
        
        print("游戏开始！人类执黑棋先手，AI执白棋。")
    
    def handle_human_move(self, x, y):
        """
        处理人类玩家落子请求
        
        :param x: 棋盘x坐标（列，0开始）
        :param y: 棋盘y坐标（行，0开始）
        :return: bool，是否成功落子
        """
        # 检查游戏是否处于活跃状态
        if not self.game_active:
            return False
        
        # 检查是否轮到人类玩家 - BoardState.current_player属性获取当前应该下棋的玩家
        if self.board_state.current_player != self.human_player:
            print("现在不是你的回合！")
            return False
        
        # BoardState.move() - 尝试在指定位置落子
        # 该方法会自动检查位置有效性、更新棋盘状态、切换玩家回合
        # 返回True表示落子成功，False表示位置无效或已被占用
        if self.board_state.move(x, y):
            print(f"人类玩家在 ({x}, {y}) 落子")
            
            # 播放落子音效
            self.board_ui.play_piece_sound()
            
            # BoardState.get_board_copy() - 获取当前棋盘状态的副本
            # GomokuAI.set_board_state() - 更新AI的内部棋盘状态，保持与游戏状态同步
            self.ai.set_board_state(self.board_state.get_board_copy())
            
            # BoardState.is_game_over() - 检查游戏是否结束（胜负已分或平局）
            if self.board_state.is_game_over():
                self._handle_game_end()
            
            return True
        else:
            print(f"无法在 ({x}, {y}) 落子！")
            return False
    
    def handle_ai_move(self):
        """处理AI落子 - AI自动分析棋局并选择最佳落子位置"""
        
        # 检查游戏状态和回合
        if not self.game_active:
            return False
        
        # 双人对战模式下不需要AI
        if self.game_mode == "vs_human":
            return False
        
        if self.board_state.current_player != self.ai_player:
            return False
        
        # GomokuAI.make_decision() - AI核心决策方法
        # 参数：传入当前棋盘状态，AI会分析局面并返回最佳落子位置
        # 返回：(row, col)坐标元组，如果无法落子则返回None
        ai_move = self.ai.make_decision(self.board_state.get_board_copy())
        
        if ai_move is None:
            print("AI无法找到有效落子位置！")
            return False
        
        # 坐标转换：AI返回(row, col)格式，需要转换为BoardState使用的(x, y)格式
        row, col = ai_move
        x, y = col, row  # x对应列(col)，y对应行(row)
        
        # 调用BoardState.move()让AI落子
        if self.board_state.move(x, y):
            print(f"AI在 ({x}, {y}) 落子")
            
            # 播放落子音效
            self.board_ui.play_piece_sound()
            
            # 检查AI落子后游戏是否结束
            if self.board_state.is_game_over():
                self._handle_game_end()
            
            return True
        else:
            print(f"AI无法在 ({x}, {y}) 落子！")
            return False
    
    def _handle_game_end(self):
        """处理游戏结束 - 判断胜负并保存结果"""
        
        self.game_active = False  # 设置游戏为非活跃状态
        
        # BoardState.get_game_info() - 获取游戏状态信息字典
        # 包含：winner(胜者), current_player(当前玩家), move_count(步数)等信息
        game_info = self.board_state.get_game_info()
        
        # 根据胜者判断游戏结果
        if game_info['winner'] == self.human_player:
            result = 1  # 人类获胜
            print("恭喜！你赢了！")
        elif game_info['winner'] == self.ai_player:
            result = 0  # AI获胜  
            print("AI获胜！再试一次吧！")
        else:
            result = 2  # 平局（棋盘下满但无人获胜）
            print("平局！")
        
        # 保存游戏结果到JSON文件（不生成评语）
        self._save_game_result(result)
        
        # 存储结果供后续使用
        self.current_game_result = result
        
        # 设置游戏结束标志，让游戏循环知道需要退出
        self.game_should_end = True

    def _save_game_result(self, result):
        """
        保存游戏结果到JSON文件
        
        :param result: 游戏结果 (0=AI获胜, 1=人类获胜, 2=平局)
        """
        try:
            # 使用相对路径指向game_database目录
            results_dir = os.path.join(os.path.dirname(__file__), 'game_database')
            os.makedirs(results_dir, exist_ok=True)
            
            results_file = os.path.join(results_dir, 'results.json')
            
            # 创建结果记录
            result_record = {
                'result': result,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'human_player': self.human_player,
                'ai_player': self.ai_player,
                'move_count': len(self.board_state.move_history),
                'game_mode': self.game_mode  # 添加游戏模式信息
            }
            
            # 读取现有结果
            results_data = []
            if os.path.exists(results_file):
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results_data = json.load(f)
                        if not isinstance(results_data, list):
                            results_data = []
                except (json.JSONDecodeError, IOError):
                    results_data = []
            
            # 追加新结果
            results_data.append(result_record)
            
            # 写回文件
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)
            
            print(f"游戏结果已保存到: {results_file}")
            
        except Exception as e:
            print(f"保存游戏结果失败: {e}")

    def show_result(self):
        """显示游戏结果 - 根据游戏模式决定是否播放动画"""
        
        # 从保存的结果获取
        if hasattr(self, 'current_game_result'):
            result = self.current_game_result
        else:
            result = self._get_latest_result()
        
        if result is not None:
            # 1. 只有AI对战模式才播放动画
            if self.game_mode == "vs_ai" and self.animation_player:
                try:
                    if result == 1:  # 人类获胜
                        print("播放胜利动画")
                        self.animation_player.play_victory_animation()
                    elif result == 0:  # AI获胜
                        print("播放失败动画")
                        self.animation_player.play_defeat_animation()
                    # 平局(result==2)不播放动画
                except Exception as e:
                    print(f"播放动画失败: {e}")
            
            # 2. 然后显示评语窗口
            # 准备用于评语生成的数据，确保类型转换
            board_state_for_comment = [[int(cell) for cell in row] for row in self.board_state.board]
            move_history_for_comment = [[int(move[0]), int(move[1]), int(move[2])] for move in self.board_state.move_history]
            
            # 显示结果窗口，包含异步评语生成和打字机效果
            result_confirmed, generated_comment = self.game_ui.show_result_menu_with_async_comment(
                result=result, 
                board_state=board_state_for_comment,
                move_history=move_history_for_comment,
                commentator=self.commentator
            )
            
            # 在后台线程中保存历史记录，避免阻塞UI
            if generated_comment:
                self._save_history_async(generated_comment, result)
            else:
                self._save_history_async("这是一场精彩的对弈！", result)
            
            return result_confirmed
        return True

    def _save_history_async(self, comment, result):
        """
        异步保存历史记录，避免阻塞UI
        
        :param comment: 评语
        :param result: 游戏结果
        """
        import threading
        
        def save_history():
            try:
                # 转换数据类型以确保JSON序列化兼容
                safe_result = int(result) if result is not None else 0
                safe_comment = str(comment) if comment else "这是一场精彩的对弈！"
                
                # 添加游戏模式信息到历史记录
                self.board_state.save_to_history_with_mode(
                    custom_comment=safe_comment, 
                    game_result=safe_result,
                    game_mode=self.game_mode
                )
                print("完整游戏记录已保存")
            except Exception as e:
                print(f"保存完整记录失败: {e}")
                # 保存基本记录
                try:
                    self.board_state.save_to_history(custom_comment="这是一场精彩的对弈！", game_result=int(result) if result is not None else 0)
                    print("基本游戏记录已保存")
                except Exception as e2:
                    print(f"保存基本记录也失败: {e2}")
        
        # 创建后台线程保存历史记录
        save_thread = threading.Thread(target=save_history)
        save_thread.daemon = True
        save_thread.start()

    def _get_latest_result(self):
        """
        获取最新的游戏结果
        
        :return: int or None，最新的游戏结果
        """
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'game_database', 'results.json')
            
            if not os.path.exists(results_file):
                return None
            
            with open(results_file, 'r', encoding='utf-8') as f:
                results_data = json.load(f)
                
            if isinstance(results_data, list) and results_data:
                # 返回最新（最后一个）结果
                return results_data[-1]['result']
                
        except Exception as e:
            print(f"读取游戏结果失败: {e}")
        
        return None

    def show_history(self):
        """显示历史对局记录"""
        try:
            # 确保游戏屏幕已初始化
            if self.screen is None:
                self._init_game_screen()
            
            # 创建历史记录UI实例
            history_ui = HistoryUI(self.screen)
            # 运行历史记录界面
            history_ui.run()
            
            # 历史记录界面退出后，不需要特殊处理，会自动返回主菜单循环
            
        except Exception as e:
            print(f"显示历史记录失败: {e}")
            # 如果失败，创建临时屏幕显示错误信息
            temp_screen = pygame.display.set_mode((800, 600))
            temp_screen.fill((255, 255, 255))
            font = pygame.font.Font(None, 36)
            error_text = font.render(f"历史记录加载失败: {str(e)}", True, (255, 0, 0))
            text_rect = error_text.get_rect(center=(400, 300))
            temp_screen.blit(error_text, text_rect)
            pygame.display.flip()
            pygame.time.wait(2000)  # 显示2秒错误信息

    def run_game_loop(self):
        """运行游戏主循环 - 处理游戏进行中的逻辑"""
        
        # 初始化游戏屏幕和UI
        self._init_game_screen()
        
        # 开始新游戏
        self.start_game()
        
        ai_think_delay = 0  # AI思考延迟计数器，用于模拟AI思考时间
        self.game_should_end = False  # 游戏结束标志
        game_end_display_time = 0  # 游戏结束后的显示时间
        
        while self.running:
            # 处理所有pygame事件（键盘、鼠标、窗口等）
            if not self._handle_events():
                break  # 如果返回False则退出游戏循环
            
            # 检查游戏是否应该结束
            if self.game_should_end:
                # 显示游戏结果一段时间后自动返回菜单
                game_end_display_time += 1
                if game_end_display_time > 180:  # 显示3秒（180帧 / 60FPS）
                    break  # 退出游戏循环，返回主菜单
            
            # AI回合处理（仅在AI对战模式下）
            if (self.game_mode == "vs_ai" and self.game_active and 
                self.board_state.current_player == self.ai_player):
                
                # 添加人工延迟，让AI看起来在"思考"
                # 提升用户体验，避免AI瞬间落子
                ai_think_delay += 1
                if ai_think_delay > 30:  # 约0.5秒延迟（30帧 / 60FPS）
                    self.handle_ai_move()
                    ai_think_delay = 0
            else:
                ai_think_delay = 0  # 非AI回合时重置延迟计数器
            
            # 绘制游戏画面
            self._draw_game()
            
            # 控制游戏帧率为60FPS
            self.clock.tick(60)

    def run(self):
        """运行游戏主程序 - 管理整个游戏的生命周期"""
        
        try:
            # 主程序循环：菜单 -> 游戏 -> 结果 -> 菜单...
            while self.running:
                # GameUI.show_start_menu() - 显示开始菜单
                # 返回用户选择："start"(开始游戏), "history"(历史记录), "settings"(设置), "quit"(退出)
                choice = self.game_ui.show_start_menu()
                
                if choice == "start":
                    # 显示游戏模式选择界面
                    mode_choice = self.show_mode_selection()
                    
                    if mode_choice == "vs_ai":
                        self.game_mode = "vs_ai"
                        self.run_game_loop()
                        # 游戏结束后显示结果，等待用户确认
                        if hasattr(self, 'game_should_end') and self.game_should_end:
                            self.show_result()
                    elif mode_choice == "vs_human":
                        self.game_mode = "vs_human"
                        self.run_game_loop()
                        # 游戏结束后显示结果，等待用户确认
                        if hasattr(self, 'game_should_end') and self.game_should_end:
                            self.show_result()
                    # 如果选择"back"或其他，回到主菜单
                
                elif choice == "history":
                    # 显示历史记录
                    self.show_history()
                    
                elif choice == "settings":
                    # 显示设置界面
                    self.show_settings()
                    
                elif choice == "quit":
                    # 退出游戏
                    self.running = False
                
                else:
                    # 处理异常情况（如窗口被强制关闭）
                    self.running = False
        
        except Exception as e:
            print(f"游戏运行错误: {e}")
        
        finally:
            # 清理资源：关闭pygame窗口，退出程序
            # GameUI.quit() - 调用pygame.quit()和sys.exit()
            self.game_ui.quit()

    def show_mode_selection(self):
        """显示游戏模式选择界面"""
        try:
            # 确保游戏屏幕已初始化
            if self.screen is None:
                self._init_game_screen()
            
            # 确保模式选择UI已初始化
            if self.mode_selection_ui is None:
                self._init_mode_selection_ui()
            
            # 显示模式选择界面
            if self.mode_selection_ui:
                return self.mode_selection_ui.show()
            else:
                print("模式选择UI初始化失败")
                return "back"
                
        except Exception as e:
            print(f"显示模式选择界面失败: {e}")
            return "back"

    def _draw_game(self):
        """绘制游戏画面 - 渲染棋盘、棋子和游戏信息"""
        
        # 完全清除屏幕
        self.screen.fill((0, 0, 0))  # 用黑色清除屏幕
        
        # 先绘制背景 - 删除任何可能的调试输出
        self.board_ui.draw_background()
        
        # BoardUI.draw_board() - 绘制棋盘网格
        self.board_ui.draw_board()
        
        # BoardUI.draw_pieces() - 根据棋盘状态绘制所有棋子
        # 参数：board_state.board是二维数组，0=空位，1=黑棋，2=白棋
        self.board_ui.draw_pieces(self.board_state.board)
        
        # 绘制最后一步棋的标记（红色圆圈）
        # BoardState.get_last_move() - 获取最后一步棋的信息 (x, y, player)
        last_move = self.board_state.get_last_move()
        if last_move:
            x, y, _ = last_move  # 只需要坐标，忽略玩家信息
            # BoardUI.draw_last_move_marker() - 在指定位置绘制最后一步标记
            self.board_ui.draw_last_move_marker((x, y))
        
        # 准备游戏状态文本
        game_info = self.board_state.get_game_info()
        game_status = ""
        
        # 根据游戏状态显示不同的提示信息
        if game_info['is_game_over']:
            if self.game_mode == "vs_human":
                # 双人对战模式
                if game_info['winner'] == 1:
                    game_status = "Black Wins!"
                elif game_info['winner'] == 2:
                    game_status = "White Wins!"
                else:
                    game_status = "Draw!"
            else:
                # AI对战模式
                if game_info['winner'] == self.human_player:
                    game_status = "You Win!"
                elif game_info['winner'] == self.ai_player:
                    game_status = "AI Wins!"
                else:
                    game_status = "Draw!"
        elif self.game_mode == "vs_human":
            # 双人对战模式显示当前玩家
            if self.board_state.current_player == 1:
                game_status = "Black's Turn"
            else:
                game_status = "White's Turn"
        elif self.board_state.current_player == self.ai_player:
            game_status = "AI Thinking..."  # AI思考中提示
        
        # BoardUI.draw_game_info() - 绘制游戏信息栏
        # 参数：当前玩家、步数、游戏状态文本
        self.board_ui.draw_game_info(
            current_player=self.board_state.current_player,
            move_count=game_info['move_count'],
            game_status=game_status
        )
        
        # BoardUI.update_display() - 更新屏幕显示（调用pygame.display.flip()）
        self.board_ui.update_display()

    def _handle_events(self):
        """
        处理pygame事件 - 键盘输入和鼠标点击
        
        :return: bool，是否继续游戏循环
        """
        for event in pygame.event.get():
            # 处理窗口关闭事件
            if event.type == pygame.QUIT:
                return False
            
            # 处理键盘按键事件
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R键 - 重新开始游戏
                    self.start_game()
                    
                elif event.key == pygame.K_u:  # U键 - 悔棋功能
                    if self.game_active:
                        # BoardState.undo_move() - 撤销最后一步棋
                        # 返回True表示悔棋成功，False表示无棋可悔
                        if self.board_state.undo_move():
                            # 如果悔棋后轮到AI，再悔一步（撤销AI的棋）
                            # 这样保证悔棋后始终轮到人类玩家
                            if (self.board_state.current_player == self.ai_player and 
                                len(self.board_state.move_history) > 0):
                                self.board_state.undo_move()
                        
                            # 更新AI的棋盘状态，保持同步
                            self.ai.set_board_state(self.board_state.get_board_copy())
                            print("悔棋成功！")
                            
                elif event.key == pygame.K_ESCAPE:  # ESC键 - 退出到主菜单
                    return False
            
            # 处理鼠标点击事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.game_active:  # 左键点击且游戏进行中
                    mouse_pos = pygame.mouse.get_pos()  # 获取鼠标位置(像素坐标)
                    
                    # BoardUI.get_click_position() - 将像素坐标转换为棋盘坐标
                    # 返回(x, y)棋盘坐标，如果点击位置无效则返回None
                    board_pos = self.board_ui.get_click_position(mouse_pos)
                    
                    if board_pos:
                        x, y = board_pos
                        # 处理人类玩家的落子请求
                        self.handle_human_move(x, y)
        
        return True  # 继续游戏循环

    def show_settings(self):
        """显示设置界面"""
        try:
            # 确保游戏屏幕已初始化
            if self.screen is None:
                self._init_game_screen()
            
            # 确保设置UI已初始化
            if self.setting_ui is None:
                self._init_setting_ui()
            
            # 显示设置界面
            if self.setting_ui:
                self.setting_ui.show()
            else:
                print("设置UI初始化失败")
                
        except Exception as e:
            print(f"显示设置界面失败: {e}")
            # 如果失败，创建临时屏幕显示错误信息
            temp_screen = pygame.display.set_mode((800, 600))
            temp_screen.fill((255, 255, 255))
            font = pygame.font.Font(None, 36)
            error_text = font.render(f"Settings load failed: {str(e)}", True, (255, 0, 0))
            text_rect = error_text.get_rect(center=(400, 300))
            temp_screen.blit(error_text, text_rect)
            pygame.display.flip()
            pygame.time.wait(2000)  # 显示2秒错误信息

def main():
    """
    主函数 - 程序入口点
    创建游戏实例并启动游戏
    """
    try:
        # 创建游戏实例
        # 参数：棋盘大小15x15（标准五子棋棋盘），初始窗口尺寸800x600
        game = GomokuGame(
            board_size=15,
            screen_width=800,
            screen_height=600
        )
        
        # 启动游戏主程序
        game.run()
        
    except Exception as e:
        # 捕获启动时的异常，提供错误信息
        print(f"程序启动失败: {e}")
        input("按任意键退出...")


# Python脚本入口点
if __name__ == "__main__":
    main()
    main()
