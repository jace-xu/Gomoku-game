import numpy as np
import random
from collections import defaultdict


class GomokuAI:
    """优化版五子棋AI：优先堵截对手三四阵型"""

    # 评分常量（提高获胜权重）
    FIVE = 1000000
    OPP_OPEN_FOUR = 900000
    OPP_FOUR = 850000
    OPP_OPEN_THREE = 750000
    OPP_JUMP_THREE = 650000
    OPP_SPLIT_THREE = 650000
    OPP_THREE = 50000
    OPP_TWO = 10000
    OPP_ONE = 1

    MY_OPEN_FOUR = 900000
    MY_FOUR = 850000
    MY_OPEN_THREE = 350000
    MY_JUMP_THREE = 250000
    MY_SPLIT_THREE = 250000
    MY_THREE = 25000
    MY_TWO = 10000
    MY_ONE = 1

    # 搜索参数
    SEARCH_DEPTH = 2
    DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
    DEFENSE_WEIGHT = 4.0
    DIAGONAL_PRIORITY = True
    PROXIMITY_WEIGHT = 3000
    OFFENSIVE_BONUS = 1.8
    MAX_SCORE_LIMIT = 1000000000
    TRAP_BONUS = 500000
    WINNING_PRIORITY = 10000000  # 获胜位置额外优先级
    DOUBLE_THREAT_BONUS = 300000  # 双威胁额外权重
    COMBO_THREAT_BONUS = 800000  # 组合威胁额外权重（提高优先级）

    def __init__(self, board_size=15, ai_player=2, human_player=1):
        self.board_size = board_size
        self.ai_player = ai_player
        self.human_player = human_player
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.best_move = None
        self.threat_space = set()
        self.diagonal_threats = defaultdict(int)
        
        # 历史表和其他缺失的属性
        self.history_table = {}  # 历史启发式表
        self.killer_moves = [[] for _ in range(10)]  # 杀手移动表
        self.transposition_table = {}  # 置换表
        
        # 难度相关设置
        self.difficulty_level = 2  # 默认难度：Normal (1=Easy, 2=Normal, 3=Hard)
        self.use_random_strategy = False  # 是否使用随机策略
        self._update_difficulty_settings()
        
        self.reset_board()

    def _update_difficulty_settings(self):
        """根据难度等级更新AI参数"""
        if self.difficulty_level == 1:  # Easy - 随机下棋
            self.SEARCH_DEPTH = 0  # 不使用搜索
            self.DEFENSE_WEIGHT = 0.5  # 几乎不防守
            self.PROXIMITY_WEIGHT = 100  # 降低邻近权重
            self.COMBO_THREAT_BONUS = 10000  # 大幅降低威胁检测
            self.WINNING_PRIORITY = 100000  # 降低获胜优先级
            self.use_random_strategy = True  # 启用随机策略
        elif self.difficulty_level == 2:  # Normal
            self.SEARCH_DEPTH = 2
            self.DEFENSE_WEIGHT = 4.0
            self.PROXIMITY_WEIGHT = 3000
            self.COMBO_THREAT_BONUS = 800000
            self.WINNING_PRIORITY = 10000000
            self.use_random_strategy = False
        elif self.difficulty_level == 3:  # Hard
            self.SEARCH_DEPTH = 3
            self.DEFENSE_WEIGHT = 6.0
            self.PROXIMITY_WEIGHT = 5000
            self.COMBO_THREAT_BONUS = 1200000
            self.WINNING_PRIORITY = 15000000
            self.use_random_strategy = False
        
        print(f"AI难度已设置为级别 {self.difficulty_level}, 搜索深度: {self.SEARCH_DEPTH}, 随机策略: {getattr(self, 'use_random_strategy', False)}")

    def set_difficulty_level(self, level):
        """
        设置AI难度等级
        :param level: 难度等级 (1=Easy, 2=Normal, 3=Hard)
        """
        if level in [1, 2, 3]:
            self.difficulty_level = level
            self._update_difficulty_settings()
            return True
        else:
            print(f"无效的难度等级: {level}，应该是 1(Easy), 2(Normal), 或 3(Hard)")
            return False

    def set_difficulty(self, level):
        """兼容方法：设置难度"""
        return self.set_difficulty_level(level)

    def get_difficulty_level(self):
        """获取当前难度等级"""
        return self.difficulty_level

    def get_difficulty_name(self):
        """获取当前难度名称"""
        difficulty_names = {1: "Easy", 2: "Normal", 3: "Hard"}
        return difficulty_names.get(self.difficulty_level, "Unknown")

    def set_board_state(self, board):
        if isinstance(board, list):
            board = np.array(board)
        self.board = board.copy().astype(int)
        self._update_threat_space()

    def _update_threat_space(self):
        self.threat_space = set()
        self.diagonal_threats.clear()

        # 检查已有棋子周围3格内的空位
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] != 0:
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            if dx == 0 and dy == 0:
                                continue
                            x, y = i + dx, j + dy
                            if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == 0:
                                self.threat_space.add((x, y))
                                if abs(dx) == abs(dy):
                                    self.diagonal_threats[(x, y)] += 2
                                else:
                                    self.diagonal_threats[(x, y)] += 1

    def get_valid_moves(self):
        if self.threat_space:
            threat_moves = list(self.threat_space)
            threat_moves.sort(key=lambda pos: self.diagonal_threats.get(pos, 0), reverse=True)
            return threat_moves

        human_pos = np.argwhere(self.board == self.human_player)
        ai_pos = np.argwhere(self.board == self.ai_player)
        all_pos = np.vstack((human_pos, ai_pos)) if human_pos.size > 0 and ai_pos.size > 0 else human_pos

        if all_pos.size > 0:
            adjacent = set()
            for (i, j) in all_pos:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        x, y = i + dx, j + dy
                        if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == 0:
                            adjacent.add((x, y))
            if adjacent:
                return list(adjacent)

        center = self.board_size // 2
        return [(i, j) for i in range(center - 2, center + 3)
                for j in range(center - 2, center + 3)
                if self.board[i][j] == 0]

    def evaluate_position(self):
        threat_score = self._evaluate_player_threat(self.human_player, defensive=True) * self.DEFENSE_WEIGHT
        offense_score = self._evaluate_player_threat(self.ai_player, defensive=False)

        # 检测陷阱模式并增加额外奖励
        trap_score = self._detect_trap_patterns()
        return offense_score - threat_score + trap_score

    def _detect_trap_patterns(self):
        """检测三子一行两子一行的陷阱模式"""
        trap_score = 0

        # 检测横向陷阱
        for i in range(self.board_size):
            for j in range(self.board_size - 5):
                # 三子一行
                if (self.board[i][j] == self.human_player and
                        self.board[i][j + 1] == self.human_player and
                        self.board[i][j + 2] == self.human_player and
                        self.board[i][j + 3] == 0):  # 空位是关键

                    # 检查下方是否有两子
                    if i < self.board_size - 1:
                        if (self.board[i + 1][j + 3] == self.human_player and
                                self.board[i + 1][j + 4] == self.human_player):
                            trap_score += self.TRAP_BONUS

                    # 检查上方是否有两子
                    if i > 0:
                        if (self.board[i - 1][j + 3] == self.human_player and
                                self.board[i - 1][j + 4] == self.human_player):
                            trap_score += self.TRAP_BONUS

        # 检测纵向陷阱
        for i in range(self.board_size - 5):
            for j in range(self.board_size):
                # 三子一列
                if (self.board[i][j] == self.human_player and
                        self.board[i + 1][j] == self.human_player and
                        self.board[i + 2][j] == self.human_player and
                        self.board[i + 3][j] == 0):  # 空位是关键

                    # 检查右侧是否有两子
                    if j < self.board_size - 1:
                        if (self.board[i + 3][j + 1] == self.human_player and
                                self.board[i + 3][j + 2] == self.human_player):
                            trap_score += self.TRAP_BONUS

                    # 检查左侧是否有两子
                    if j > 0:
                        if (self.board[i + 3][j - 1] == self.human_player and
                                self.board[i + 3][j - 2] == self.human_player):
                            trap_score += self.TRAP_BONUS

        return trap_score

    def _evaluate_player_threat(self, player, defensive=True):
        score = 0

        # 对角线方向优先检测
        if self.DIAGONAL_PRIORITY:
            for dx, dy in [(1, 1), (1, -1)]:
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        if self.board[i][j] == player:
                            score += self._evaluate_pattern(i, j, dx, dy, player, defensive)

        # 水平和垂直方向检测
        for dx, dy in [(1, 0), (0, 1)]:
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] == player:
                        score += self._evaluate_pattern(i, j, dx, dy, player, defensive)
        return score

    def _evaluate_pattern(self, i, j, dx, dy, player, defensive):
        pattern = []
        for k in range(-5, 6):
            x = i + k * dx
            y = j + k * dy
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                pattern.append(self.board[x][y])
            else:
                pattern.append(self.human_player if player == self.ai_player else self.ai_player)

        pattern_str = ''.join(['P' if p == player else ('O' if p != 0 else 'E') for p in pattern])

        if player == self.human_player and defensive:
            if 'PPPPP' in pattern_str:
                return self.FIVE
            if 'EPPPPE' in pattern_str:
                return self.OPP_OPEN_FOUR
            if 'EPPPP' in pattern_str or 'PPPPE' in pattern_str:
                return self.OPP_FOUR
            if 'EPPPE' in pattern_str:
                return self.OPP_OPEN_THREE
            if 'PEPPE' in pattern_str:
                return self.OPP_SPLIT_THREE

            segments = self._find_segments(pattern, player)
            for seg in segments:
                length, left_open, right_open = seg
                if length >= 5:
                    return self.FIVE
                elif length == 4:
                    if left_open and right_open:
                        return self.OPP_OPEN_FOUR
                    elif left_open or right_open:
                        return self.OPP_FOUR
                elif length == 3:
                    if left_open and right_open:
                        return self.OPP_OPEN_THREE
            return 0
        elif player == self.ai_player and not defensive:
            if 'W' * 4 in pattern_str:
                return self.MY_OPEN_FOUR * 2
            if 'EWWWE' in pattern_str:
                return self.MY_OPEN_FOUR
            if 'EWWW' in pattern_str or 'WWWE' in pattern_str:
                return self.MY_FOUR

            segments = self._find_segments(pattern, player)
            for seg in segments:
                length, left_open, right_open = seg
                if length >= 5:
                    return self.MY_OPEN_FOUR * 2
                elif length == 4:
                    if left_open and right_open:
                        return self.MY_OPEN_FOUR
                    elif left_open or right_open:
                        return self.MY_FOUR
                elif length == 3:
                    if left_open and right_open:
                        return self.MY_OPEN_THREE
            return 0
        else:
            return 0

    def _find_segments(self, pattern, player):
        segments = []
        start = -1
        for idx, p in enumerate(pattern):
            if p == player:
                if start == -1:
                    start = idx
            else:
                if start != -1:
                    end = idx - 1
                    left_open = (start == 0) or (pattern[start - 1] != player)
                    right_open = (end == len(pattern) - 1) or (pattern[end + 1] != player)
                    segments.append((end - start + 1, left_open, right_open))
                    start = -1
        if start != -1:
            end = len(pattern) - 1
            left_open = (start == 0) or (pattern[start - 1] != player)
            right_open = (end == len(pattern) - 1) or (pattern[end + 1] != player)
            segments.append((end - start + 1, left_open, right_open))
        return segments

    def _check_urgent_moves(self):
        defensive_moves = defaultdict(list)
        offensive_moves = defaultdict(list)

        # 1. 优先检测AI的必胜机会（WIN）
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] != self.ai_player:
                    continue

                for dx, dy in self.DIRECTIONS:
                    threat_type, block_moves = self._detect_threat_in_direction(i, j, dx, dy, self.ai_player)
                    if threat_type == 'WIN':
                        return 'offense', block_moves  # 立即返回必胜机会

        # 2. 检测对手的致命威胁（五连和活四）
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] != self.human_player:
                    continue

                for dx, dy in self.DIRECTIONS:
                    threat_type, block_moves = self._detect_threat_in_direction(i, j, dx, dy, self.human_player)
                    if threat_type in ['FIVE', 'OPEN_FOUR']:
                        for move in block_moves:
                            if move not in defensive_moves[threat_type]:
                                defensive_moves[threat_type].append(move)

        # 如果有五连或活四威胁，立即返回
        if defensive_moves.get('FIVE') or defensive_moves.get('OPEN_FOUR'):
            return 'defense', defensive_moves.get('FIVE', []) + defensive_moves.get('OPEN_FOUR', [])

        return None, []

    def _detect_threat_in_direction(self, i, j, dx, dy, player=None):
        if player is None:
            player = self.human_player

        pattern = []
        for k in range(-5, 6):
            x = i + k * dx
            y = j + k * dy
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                pattern.append(self.board[x][y])
            else:
                pattern.append(self.ai_player if player == self.human_player else self.human_player)

        return None, []

    def find_best_move(self):
        """寻找最佳移动，根据难度采用不同策略"""
        # Easy难度：使用随机策略
        if self.difficulty_level == 1 and getattr(self, 'use_random_strategy', False):
            return self._random_move_strategy()
        
        # Normal和Hard难度：使用原有的智能策略
        move_type, urgent_moves = self._check_urgent_moves()
        if urgent_moves:
            if move_type == 'defense':
                # 对于防守移动，直接返回最高优先级的位置
                return urgent_moves[0] if urgent_moves else None
            else:
                # 对于进攻移动，选择评分最高的位置
                sorted_moves = self._sort_moves(urgent_moves, self.ai_player)
                return sorted_moves[0] if sorted_moves else random.choice(urgent_moves)

        # 检查是否有立即获胜的机会
        winning_move = self._find_winning_move()
        if winning_move:
            return winning_move

        # 使用搜索算法（仅在非随机模式下）
        if self.SEARCH_DEPTH > 0:
            _, move = self.alpha_beta(self.SEARCH_DEPTH, -float('inf'), float('inf'), True)
            if move:
                return move

        # 随机选择一个有效移动
        valid_moves = self.get_valid_moves()
        return random.choice(valid_moves) if valid_moves else None

    def _random_move_strategy(self):
        """随机下棋策略（Easy难度专用）"""
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None
        
        # 80%概率完全随机，20%概率稍微智能一点
        if random.random() < 0.8:
            # 完全随机选择
            return random.choice(valid_moves)
        else:
            # 稍微倾向于在已有棋子附近下棋
            human_pos = np.argwhere(self.board == self.human_player)
            ai_pos = np.argwhere(self.board == self.ai_player)
            
            if len(human_pos) > 0 or len(ai_pos) > 0:
                # 在已有棋子周围寻找位置
                nearby_moves = []
                all_pos = np.vstack((human_pos, ai_pos)) if len(human_pos) > 0 and len(ai_pos) > 0 else (human_pos if len(human_pos) > 0 else ai_pos)
                
                for pos in all_pos:
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            if dx == 0 and dy == 0:
                                continue
                            new_pos = (pos[0] + dx, pos[1] + dy)
                            if new_pos in valid_moves:
                                nearby_moves.append(new_pos)
                
                if nearby_moves:
                    return random.choice(nearby_moves)
            
            # 如果没有找到附近的位置，就随机选择
            return random.choice(valid_moves)

    def alpha_beta(self, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.evaluate_position(), None

        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return 0, None

        if maximizing_player:
            max_eval = -float('inf')
            best_move = None
            sorted_moves = self._sort_moves(valid_moves, self.ai_player)[:10]
            for move in sorted_moves:
                row, col = move
                self.board[row][col] = self.ai_player
                current_eval, _ = self.alpha_beta(depth - 1, alpha, beta, False)
                self.board[row][col] = 0
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = move
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            sorted_moves = self._sort_moves(valid_moves, self.human_player)[:10]
            for move in sorted_moves:
                row, col = move
                self.board[row][col] = self.human_player
                current_eval, _ = self.alpha_beta(depth - 1, alpha, beta, True)
                self.board[row][col] = 0
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_move = move
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def _sort_moves(self, moves, player):
        move_scores = []

        human_pos = np.argwhere(self.board == self.human_player)
        ai_pos = np.argwhere(self.board == self.ai_player)
        all_pos = np.vstack((human_pos, ai_pos)) if human_pos.size > 0 and ai_pos.size > 0 else human_pos

        for move in moves:
            row, col = move
            self.board[row][col] = player
            eval_score = self.evaluate_position()
            self.board[row][col] = 0

            proximity_bonus = 0
            if all_pos.size > 0:
                min_distance = float('inf')
                for pos in all_pos:
                    distance = abs(pos[0] - row) + abs(pos[1] - col)
                    if distance < min_distance:
                        min_distance = distance
                proximity_bonus = self.PROXIMITY_WEIGHT / (min_distance + 1)

            defense_bonus = abs(eval_score) * 0.2 if eval_score < 0 else 0
            total_score = eval_score + proximity_bonus + defense_bonus
            move_scores.append((total_score, move))

        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in move_scores]

    def _find_winning_move(self):
        """寻找立即获胜的落子位置"""
        for move in self.get_valid_moves():
            row, col = move
            # 检查落子后是否形成五连
            if self._is_winning_move(row, col):
                return (row, col)
        return None

    def _is_winning_move(self, row, col):
        """检查落子后是否形成五连"""
        # 临时落子
        self.board[row][col] = self.ai_player

        # 检查所有方向
        for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            count = 1  # 当前落子已经算1

            # 正向检查
            for k in range(1, 5):
                x, y = row + k * direction[0], col + k * direction[1]
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == self.ai_player:
                    count += 1
                else:
                    break

            # 反向检查
            for k in range(1, 5):
                x, y = row - k * direction[0], col - k * direction[1]
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == self.ai_player:
                    count += 1
                else:
                    break

            if count >= 5:
                # 恢复棋盘
                self.board[row][col] = 0
                return True

        # 恢复棋盘
        self.board[row][col] = 0
        return False

    def make_decision(self, board_state=None):
        if board_state is not None:
            self.set_board_state(board_state)
        return self.find_best_move()

    def update_board(self, row, col, player):
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == 0:
            self.board[row][col] = player
            self._update_threat_space()
            return True
        return False

    def is_valid_position(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == 0

    def get_empty_positions(self):
        empty_positions = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    empty_positions.append((row, col))
        return empty_positions

    def reset_board(self):
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.threat_space = set()
        self.diagonal_threats.clear()
        self.history_table.clear()  # 清空历史表
        self.killer_moves = [[] for _ in range(10)]  # 重置杀手移动表
        self.transposition_table.clear()  # 清空置换表