import os
import json
from datetime import datetime

# 尝试导入comment模块，如果失败则设置为None
try:
    from logic.comment import generate_comment
    COMMENT_AVAILABLE = True
except ImportError:
    generate_comment = None
    COMMENT_AVAILABLE = False

class BoardState:
    def __init__(self, size=15, ai_player=2, human_player=1, first_player=1):
        """
        初始化棋盘状态对象。

        :param size: 棋盘边长，默认15（15x15）
        :param ai_player: AI执子编号（1=黑，2=白），默认2（白）
        :param human_player: 人类执子编号（1=黑，2=白），默认1（黑）
        :param first_player: 首手玩家编号（1或2），默认1（黑先）
        """
        if ai_player == human_player:
            raise ValueError("AI玩家和人类玩家编号不能相同")
        if ai_player not in [1, 2] or human_player not in [1, 2]:
            raise ValueError("玩家编号必须是1或2")
        if first_player not in [1, 2]:
            raise ValueError("首手玩家编号必须是1或2")
        if size < 5 or size > 30:
            raise ValueError("棋盘大小必须在5-30之间")

        self.size = size  # 棋盘边长
        self.ai_player = ai_player  # AI执子
        self.human_player = human_player  # 人类执子
        self.board = None  # 棋盘二维数组，后续在reset中初始化
        self.move_history = None  # 保存落子历史，便于悔棋或复盘
        self.current_player = None  # 记录当前轮到哪方
        self.winner = None  # 胜者编号，None表示未分胜负
        self.reset(first_player)  # 初始化棋盘和其它状态

    def reset(self, first_player=1):
        """
        重置棋盘和对局状态。可指定先手玩家。

        :param first_player: 先手玩家编号（1或2）
        """
        if first_player not in [1, 2]:
            raise ValueError("首手玩家编号必须是1或2")

        self.board = [[0] * self.size for _ in range(self.size)]  # 0表示空，1/2分别代表黑/白
        self.move_history = []  # 清空历史记录
        self.current_player = first_player  # 重新设定先手
        self.winner = None  # 清空胜负标记

    def is_valid_position(self, x, y):
        """
        检查位置是否有效且为空

        :param x: 横坐标（列号，0开始）
        :param y: 纵坐标（行号，0开始）
        :return: bool
        """
        return (0 <= x < self.size and
                0 <= y < self.size and
                self.board[y][x] == 0)

    def get_board_copy(self):
        """
        获取棋盘状态的副本

        :return: 二维列表，棋盘状态副本
        """
        return [row[:] for row in self.board]

    def get_empty_positions(self):
        """
        获取所有空位置

        :return: 空位置坐标列表 [(x, y), ...]
        """
        empty_positions = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == 0:
                    empty_positions.append((x, y))
        return empty_positions

    def move(self, x, y, player=None):
        """
        在(x, y)坐标落子

        :param x: 横坐标（列号，0开始）
        :param y: 纵坐标（行号，0开始）
        :param player: 玩家编号，如果为None则使用当前玩家
        :return: bool，是否成功落子
        """
        if player is None:
            player = self.current_player

        if not self.is_valid_position(x, y):
            return False

        if self.winner is not None:
            return False

        self.board[y][x] = player
        self.move_history.append((x, y, player))

        if self.check_win(x, y, player):
            self.winner = player

        # 只有在使用当前玩家时才切换玩家
        if player == self.current_player:
            self.current_player = 3 - self.current_player

        return True

    def check_win(self, x, y, player):
        """
        检查以(x, y)为落点，player是否形成五子连珠。

        :param x: 落子横坐标
        :param y: 落子纵坐标
        :param player: 检查的玩家编号（1或2）
        :return: True if 胜负已分，否则False
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            for d in (1, -1):
                for i in range(1, 5):
                    nx, ny = x + dx * i * d, y + dy * i * d
                    if 0 <= nx < self.size and 0 <= ny < self.size and self.board[ny][nx] == player:
                        count += 1
                    else:
                        break
            if count >= 5:
                return True
        return False

    def is_game_over(self):
        """
        检查棋局是否结束（分出胜负或盘满）。

        :return: True if 已结束，否则False
        """
        return self.winner is not None or self.is_full()

    def is_full(self):
        """
        检查棋盘是否已满。

        :return: True if 所有格子都不为0，否则False
        """
        return all(cell != 0 for row in self.board for cell in row)

    def undo_move(self):
        """
        悔棋：撤销最后一步操作

        :return: bool，是否成功悔棋
        """
        if not self.move_history:
            return False

        x, y, player = self.move_history.pop()
        self.board[y][x] = 0
        self.current_player = player
        self.winner = None
        return True

    def get_game_info(self):
        """
        获取游戏状态信息

        :return: dict，包含游戏状态信息
        """
        return {
            'size': self.size,
            'current_player': self.current_player,
            'winner': self.winner,
            'move_count': len(self.move_history),
            'is_game_over': self.is_game_over(),
            'is_full': self.is_full(),
            'ai_player': self.ai_player,
            'human_player': self.human_player
        }

    def get_last_move(self):
        """
        获取最后一步棋的信息

        :return: tuple or None，(x, y, player) 或 None
        """
        if self.move_history:
            return self.move_history[-1]
        return None

    def simulate_move(self, x, y, player):
        """
        模拟落子（不改变实际棋盘状态）

        :param x: 横坐标
        :param y: 纵坐标
        :param player: 玩家编号
        :return: bool，模拟落子是否会获胜
        """
        if not self.is_valid_position(x, y):
            return False
        return self.check_win(x, y, player)

    def save_to_history(self, history_path: str = None, custom_comment: str = None, game_result: int = None) -> None:
        """
        保存当前棋局信息到历史记录文件 history.json。

        :param history_path(str, 可选)：历史文件路径。若未指定则默认保存到项目根目录下 game_database/history.json。
        :param custom_comment(str, 可选)：自定义评语。如果提供则使用此评语，否则尝试生成AI评语。
        :param game_result(int, 可选)：游戏结果 (0=AI获胜, 1=人类获胜, 2=平局)

        :return:None
        """
        # 如果未指定路径，则默认存储到相对路径的 game_database 目录
        if history_path is None:
            history_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "game_database", "history.json"
            )

        # 确保目录存在
        os.makedirs(os.path.dirname(history_path), exist_ok=True)

        # 生成对局评语
        if custom_comment:
            comment_text = custom_comment
        elif COMMENT_AVAILABLE and generate_comment is not None:
            try:
                comment_text = generate_comment(
                    [row[:] for row in self.board],
                    [list(move) for move in self.move_history],
                    game_result  # 传入游戏结果
                )
            except Exception as exc:
                print(f"评语生成失败: {exc}")
                comment_text = "下的很好"
        else:
            comment_text = "下的很好"

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comment": comment_text,
            "board": [row[:] for row in self.board],
            "moves": [list(move) for move in self.move_history],
            "result": game_result  # 添加游戏结果信息
        }

        # 读取原有历史记录
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        print("历史文件内容异常，重置为空列表")
                        data = []
            except (json.JSONDecodeError, IOError) as err:
                print(f"读取历史记录异常: {err}")
                data = []
        else:
            data = []

        # 追加本次记录并写回文件
        data.append(record)

        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as err:
            print(f"写入历史记录异常: {err}")

