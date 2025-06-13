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
        
        # 调用初始化方法
        self._init_game_components()
    
    def _init_game_components(self):
        """初始化游戏核心组件 - 创建各个模块的实例"""
        
        # 初始化GameUI：负责开始菜单和结果显示的UI管理器
        # GameUI.show_start_menu() - 显示开始菜单
        # GameUI.show_result_menu() - 显示游戏结果
        self.game_ui = GameUI(self.screen_width, self.screen_height)
        
        # 初始化BoardState：棋盘状态和游戏规则管理器
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
        
        # 初始化音频
        self._init_audio()
    
    def _init_audio(self):
        """初始化游戏音频"""
        try:
            # 设置背景音乐和落子音效（使用相对路径）
            self.board_ui.set_background_music("assets/board_bgm.mp3")
            self.board_ui.set_piece_sound("assets/piece_sound.mp3")
        except Exception as e:
            print(f"音频初始化失败: {e}")

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
        
        # 生成AI评语，传入游戏结果信息
        try:
            print("正在生成对局评语...")
            self.game_comment = self.commentator.generate_comment(
                [row[:] for row in self.board_state.board],
                [list(move) for move in self.board_state.move_history],
                result  # 传入游戏结果
            )
            print("评语生成完成")
        except Exception as e:
            print(f"评语生成失败: {e}")
            self.game_comment = self.commentator.get_fallback_comment(len(self.board_state.move_history))
        
        # 保存游戏结果到JSON文件
        self._save_game_result(result)
        
        # 保存历史记录（包含生成的评语和游戏结果）
        try:
            self.board_state.save_to_history(custom_comment=self.game_comment, game_result=result)
            print("游戏记录已保存到历史数据库")
        except Exception as e:
            print(f"保存历史记录失败: {e}")
        
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
                'move_count': len(self.board_state.move_history)
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
        """显示游戏结果 - 调用UI模块显示胜负结果和评语"""
        
        # 从JSON文件获取最新结果
        latest_result = self._get_latest_result()
        if latest_result is not None:
            # 显示结果窗口，包含评语和确认按钮
            result_confirmed = self.game_ui.show_result_menu_with_comment(
                result=latest_result, 
                comment=getattr(self, 'game_comment', '精彩的对弈！')
            )
            return result_confirmed
        return True

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
            
            # AI回合处理
            if (self.game_active and 
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
                    # 开始游戏：进入游戏主循环
                    self.run_game_loop()
                    
                    # 游戏结束后显示结果，等待用户确认
                    if hasattr(self, 'game_should_end') and self.game_should_end:
                        self.show_result()
                
                elif choice == "history":
                    # 显示历史记录
                    self.show_history()
                    
                elif choice == "settings":
                    # 设置菜单（功能预留，暂未实现）
                    print("设置功能尚未实现")
                    # 这里可以扩展：棋盘大小设置、AI难度设置、音效设置等
                    
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

    def _draw_game(self):
        """绘制游戏画面 - 渲染棋盘、棋子和游戏信息"""
        
        # BoardUI.draw_board() - 绘制棋盘网格和背景
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
            if game_info['winner'] == self.human_player:
                game_status = "You Win!"
            elif game_info['winner'] == self.ai_player:
                game_status = "AI Wins!"
            else:
                game_status = "Draw!"
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
