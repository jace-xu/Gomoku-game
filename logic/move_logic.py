import math
import time
import random

# AI配置参数
'''AI_CONFIG = {
    "MAX_TIME": 5,  # 最长思考时间（秒）
    "MAX_DEPTH": 4,  # 搜索深度
    "WIN_SCORE": 1000000,  # 胜利分数
    "AI_PLAYER": 2,  # AI玩家标识
    "HUMAN_PLAYER": 1  # 人类玩家标识
}'''
class AI_CONFIG:
    def __init__(self, MAX_TIME, MAX_DEPTH, MAX_WIN_SCORE):
     self.MAX_TIME= 5,  # 最长思考时间（秒）
     self.MAX_DEPTH= 4,  # 搜索深度
     self.WIN_SCORE= 1000000,  # 胜利分数
     self.AI_PLAYER=2,  # AI玩家标识
     self.HUMAN_PLAYER= 1  # 人类玩家标识


# 棋型评分表（强化防守权重）
'''PATTERN_SCORES = {
    # 连五（己方/对方）
    "11111": 1000000,  # 己方（人类）连五
    "22222": -1000000,  # 对方（AI）连五
    # 活四（己方进攻/对方威胁）
    "011110": 100000,  # 己方（人类）活四
    "022220": -200000,  # 对方（AI）活四
    # 冲四（己方/对方）
    "01111": 50000,  # 己方（人类）冲四
    "11110": 50000,
    "02222": -150000,  # 对方（AI）冲四
    "22220": -150000,
    # 活三（己方/对方）
    "01110": 10000,  # 己方（人类）活三
    "02220": -50000,  # 对方（AI）活三
    # 冲三（己方/对方）
    "0111": 5000,  # 己方（人类）冲三
    "1110": 5000,
    "1011": 5000,
    "1101": 5000,
    "0222": -10000,  # 对方（AI）冲三
    "2220": -10000,
    "2022": -10000,
    "2202": -10000,
    # 活二（己方/对方）
    "0110": 1000,  # 己方（人类）活二
    "0220": -2000,  # 对方（AI）活二
    # 冲二（己方/对方）
    "011": 100,  # 己方（人类）冲二
    "110": 100,
    "022": -200,  # 对方（AI）冲二
    "220": -200,
}'''
class PATTERN_SCORES :
    def __init__(self,PATTERN_SCORES11111,PATTERN_SCORES22222,PATTERN_SCORES011110,PATTERN_SCORES022220,
                 PATTERN_SCORES01111,PATTERN_SCORES11110,PATTERN_SCORES02222,
                 PATTERN_SCORES22220,PATTERN_SCORES01110,PATTERN_SCORES02220,
                 PATTERN_SCORES0111,PATTERN_SCORES1110,PATTERN_SCORES1011,
                 PATTERN_SCORES1101,PATTERN_SCORES0222,PATTERN_SCORES2220,
                 PATTERN_SCORES2022,PATTERN_SCORES2202,PATTERN_SCORES0110,
                 PATTERN_SCORES0220,PATTERN_SCORES011,PATTERN_SCORES110,
                 PATTERN_SCORES022,PATTERN_SCORES220,):
     # 连五（己方/对方）
     self.PATTERN_SCORES11111= 1000000,  # 己方（人类）连五
     self.PATTERN_SCORES22222= -1000000,  # 对方（AI）连五
     # 活四（己方进攻/对方威胁）
     self.PATTERN_SCORES011110=100000,  # 己方（人类）活四
     self.PATTERN_SCORES022220= -200000,  # 对方（AI）活四
     # 冲四（己方/对方）
     self.PATTERN_SCORES01111=50000,  # 己方（人类）冲四
     self.PATTERN_SCORES11110=50000,
     self.PATTERN_SCORES02222= -150000,  # 对方（AI）冲四
     self.PATTERN_SCORES22220= -150000,
    # 活三（己方/对方）
     self.PATTERN_SCORES01110= 10000,  # 己方（人类）活三
     self.PATTERN_SCORES02220= -50000,  # 对方（AI）活三
    # 冲三（己方/对方）
     self.PATTERN_SCORES0111= 5000,  # 己方（人类）冲三
     self.PATTERN_SCORES1110= 5000,
     self.PATTERN_SCORES1011= 5000,
     self.PATTERN_SCORES1101= 5000,
     self.PATTERN_SCORES0222= -10000,  # 对方（AI）冲三
     self.PATTERN_SCORES2220= -10000,
     self.PATTERN_SCORES2022= -10000,
     self.PATTERN_SCORES2202= -10000,
     # 活二（己方/对方）
     self.PATTERN_SCORES0110= 1000,  # 己方（人类）活二
     self.PATTERN_SCORES0220= -2000,  # 对方（AI）活二
     # 冲二（己方/对方）
     self.PATTERN_SCORES011= 100,  # 己方（人类）冲二
     self.PATTERN_SCORES110= 100,
     self.PATTERN_SCORES022= -200,  # 对方（AI）冲二
     self.PATTERN_SCORES220= -200,



class GomokuAI:
    """五子棋AI核心类，提供智能落子决策"""

    def __init__(self, board_size=15, ai_player=AI_CONFIG["AI_PLAYER"], human_player=AI_CONFIG["HUMAN_PLAYER"]):
        """
        初始化AI实例

        Args:
            board_size (int): 棋盘大小，默认15
            ai_player (int): AI玩家标识，默认2（白方）
            human_player (int): 人类玩家标识，默认1（黑方）
        """
        self.board_size = board_size
        self.ai_player = ai_player
        self.human_player = human_player
        self.position_score = self._create_position_score_table()

    def _create_position_score_table(self):
        """创建位置评分表（中心位置更重要）"""
        score_table = [[0] * self.board_size for _ in range(self.board_size)]
        center = self.board_size // 2
        for i in range(self.board_size):
            for j in range(self.board_size):
                dist = math.sqrt((i - center) ** 2 + (j - center) ** 2)
                score_table[i][j] = int((center - dist) * 10)
        return score_table

    def get_best_move(self, board, max_time=AI_CONFIG["MAX_TIME"], max_depth=AI_CONFIG["MAX_DEPTH"]):
        """
        获取AI最佳落子位置

        Args:
            board (list): 当前棋盘状态（二维列表，0=空，1=黑，2=白）
            max_time (float): 最大思考时间（秒）
            max_depth (int): 最大搜索深度

        Returns:
            tuple: 最佳落子位置 (x, y)，若没有有效位置则返回None
        """
        self.board = [row[:] for row in board]  # 复制棋盘状态
        self.start_time = time.time()
        self.max_time = max_time

        # 检测必须防守的威胁
        urgent_move = self._find_deadly_threat()
        if urgent_move:
            return urgent_move

        # 正常搜索最佳位置
        valid_moves = self._get_valid_moves()
        if not valid_moves:
            return None

        best_score = -float('inf')
        best_move = None

        # 按威胁度排序，优先评估高价值位置
        valid_moves.sort(key=lambda move: self._evaluate_move(move[0], move[1], self.ai_player), reverse=True)

        # 迭代加深搜索
        for depth in range(1, max_depth + 1):
            if time.time() - self.start_time > max_time:
                break

            current_score, current_move = self._minimax(depth, -float('inf'), float('inf'), True)

            if current_move and (best_move is None or current_score > best_score):
                best_score = current_score
                best_move = current_move

            if best_score >= AI_CONFIG["WIN_SCORE"]:
                break

        return best_move if best_move else random.choice(valid_moves)

    def _find_deadly_threat(self):
        """检测人类玩家的致命威胁（活四、冲四）"""
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] != 0:
                    continue

                # 模拟人类在此位置落子
                self.board[y][x] = self.human_player

                # 检查是否形成威胁
                if self._check_four_in_line(y, x, self.human_player):
                    self.board[y][x] = 0  # 恢复棋盘
                    return (x, y)

                self.board[y][x] = 0  # 恢复棋盘

        return None

    def _check_four_in_line(self, y, x, player):
        """检查指定位置是否形成四连珠（活四或冲四）"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            line = self._get_line(y, x, dx, dy)
            line_str = ''.join(map(str, line))

            # 检查活四和冲四模式
            for pattern in ["011110", "01111", "11110"]:
                if pattern.replace('1', str(player)) in line_str:
                    return True

        return False

    def _get_line(self, y, x, dx, dy):
        """获取指定方向的棋型字符串（包含边界处理）"""
        line = []
        for k in range(-4, 5):
            ny, nx = y + dy * k, x + dx * k
            if 0 <= ny < self.board_size and 0 <= nx < self.board_size:
                line.append(self.board[ny][nx])
            else:
                line.append(3 - self.ai_player)  # 边界视为对方棋子
        return line

    def _get_valid_moves(self):
        """获取所有有效落子位置（靠近已有棋子的位置）"""
        occupied = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.board[i][j] != 0]

        # 如果棋盘为空，返回中心点
        if not occupied:
            return [(self.board_size // 2, self.board_size // 2)]

        # 找出所有已落子位置周围的空位
        valid_moves = set()
        for i, j in occupied:
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    ni, nj = i + dy, j + dx
                    if 0 <= ni < self.board_size and 0 <= nj < self.board_size and self.board[ni][nj] == 0:
                        valid_moves.add((nj, ni))  # 转换为(x, y)格式

        # 按位置评分排序
        return sorted(valid_moves, key=lambda move: -self.position_score[move[1]][move[0]])

    def _evaluate_move(self, x, y, player):
        """评估在指定位置落子的分数"""
        if self.board[y][x] != 0:
            return -float('inf')

        # 临时落子以评估
        self.board[y][x] = player
        score = self._evaluate_position()
        self.board[y][x] = 0  # 恢复棋盘

        return score

    def _evaluate_position(self):
        """评估当前棋盘状态分数"""
        score = 0

        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] == 0:
                    continue

                player = self.board[y][x]

                # 检查四个方向的棋型
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    line = self._get_line(y, x, dx, dy)
                    line_str = ''.join(map(str, line))

                    # 检查所有可能的5子窗口
                    for start in range(5):
                        window = line_str[start:start + 5]

                        # 计算棋型分数
                        if window in PATTERN_SCORES:
                            score += PATTERN_SCORES[window] * (1 if player == self.ai_player else -1)

                            # 添加位置分数
                            if start + 2 < len(line) and 0 <= y < self.board_size and 0 <= x < self.board_size:
                                score += self.position_score[y][x] * (1 if player == self.ai_player else -1)

        return score

    def _minimax(self, depth, alpha, beta, is_maximizing):
        """带Alpha-Beta剪枝的极小极大算法"""
        # 检查时间限制
        if time.time() - self.start_time > self.max_time:
            return self._evaluate_position(), None

        # 达到最大深度或游戏结束
        if depth == 0:
            return self._evaluate_position(), None

        valid_moves = self._get_valid_moves()
        if not valid_moves:
            return self._evaluate_position(), None

        best_move = None

        if is_maximizing:
            max_score = -float('inf')

            # 按威胁度排序，优先评估高价值位置
            valid_moves.sort(key=lambda move: self._evaluate_move(move[0], move[1], self.ai_player), reverse=True)

            for move in valid_moves:
                x, y = move

                # 模拟落子
                self.board[y][x] = self.ai_player

                # 递归评估
                score, _ = self._minimax(depth - 1, alpha, beta, False)

                # 撤销落子
                self.board[y][x] = 0

                # 更新最佳分数和最佳移动
                if score > max_score:
                    max_score = score
                    best_move = move

                # Alpha-Beta剪枝
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break

            return max_score, best_move

        else:
            min_score = float('inf')

            # 按威胁度排序，优先评估高价值位置
            valid_moves.sort(key=lambda move: self._evaluate_move(move[0], move[1], self.human_player), reverse=True)

            for move in valid_moves:
                x, y = move

                # 模拟对方落子
                self.board[y][x] = self.human_player

                # 递归评估
                score, _ = self._minimax(depth - 1, alpha, beta, True)

                # 撤销落子
                self.board[y][x] = 0

                # 更新最佳分数和最佳移动
                if score < min_score:
                    min_score = score
                    best_move = move

                # Alpha-Beta剪枝
                beta = min(beta, min_score)
                if beta <= alpha:
                    break

            return min_score, best_move