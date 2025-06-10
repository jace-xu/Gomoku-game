import numpy as np
import random
import time
from collections import defaultdict


class GomokuAI:
    """五子棋AI决策模块，具有增强的评估函数和搜索算法，特别是对活三的防守能力"""

    # 棋型评分常量 - 更新为更精细的评分体系
    FIVE = 1000000  # 五连
    OPEN_FOUR = 50000  # 活四
    FOUR = 10000  # 冲四（眠四）
    DOUBLE_FOUR = 30000  # 双冲四
    OPEN_THREE = 8000  # 活三
    DOUBLE_OPEN_THREE = 20000  # 双活三
    THREE = 2000  # 眠三
    OPEN_TWO = 1000  # 活二
    DOUBLE_OPEN_TWO = 3000  # 双活二
    TWO = 100  # 眠二
    ONE = 10  # 活一
    DEFENSE_BONUS = 30000  # 防守加成（提高活三威胁的权重）

    SEARCH_DEPTH = 3  # 默认搜索深度
    MAX_DEPTH = 6  # 最大搜索深度
    TIME_LIMIT = 1.5  # 时间限制（秒）

    DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

    OPENING_BOOK = [
        [(7, 7)],  # 天元开局
        [(6, 6), (8, 8), (6, 8), (8, 6)],  # 星位开局
        [(7, 8), (8, 7), (6, 7), (7, 6)]  # 边星开局
    ]

    def __init__(self, board_size=15, ai_player=2, human_player=1):
        if ai_player == human_player:
            raise ValueError("AI玩家和人类玩家编号不能相同")
        if ai_player not in [1, 2] or human_player not in [1, 2]:
            raise ValueError("玩家编号必须是1或2")

        self.board_size = board_size
        self.ai_player = ai_player
        self.human_player = human_player
        self.move_count = 0

        self.board = np.zeros((board_size, board_size), dtype=int)

        self.best_move = None
        self.max_score = -float('inf')

        self.threat_space = set()

        self.history_table = np.zeros((board_size, board_size), dtype=int)

        self.killer_moves = [None] * (self.MAX_DEPTH + 1)

    def set_board_state(self, board):
        if isinstance(board, list):
            board = np.array(board)

        if not isinstance(board, np.ndarray):
            raise TypeError("棋盘状态必须是numpy数组或二维列表")

        if board.shape != (self.board_size, self.board_size):
            raise ValueError(f"棋盘状态必须是大小为{self.board_size}x{self.board_size}的数组")

        self.board = board.copy().astype(int)
        self.move_count = np.count_nonzero(board)

        self._update_threat_space()

    def _update_threat_space(self):
        self.threat_space = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] != 0:
                    for dx in (-3, -2, -1, 0, 1, 2, 3):
                        for dy in (-3, -2, -1, 0, 1, 2, 3):
                            if dx == 0 and dy == 0:
                                continue
                            x, y = i + dx, j + dy
                            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                                if self.board[x][y] == 0:
                                    self.threat_space.add((x, y))
        if not self.threat_space and self.board_size > 4:
            center = self.board_size // 2
            for i in range(center - 3, center + 4):
                for j in range(center - 3, center + 4):
                    if self.board[i][j] == 0:
                        self.threat_space.add((i, j))

    def get_valid_moves(self):
        return list(self.threat_space) if self.threat_space else self.get_empty_positions()

    def evaluate_position(self, player):
        score = 0
        opponent = 3 - player

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == player:
                    for dx, dy in self.DIRECTIONS:
                        score += self._evaluate_direction(i, j, dx, dy, player)
                elif self.board[i][j] == opponent:
                    for dx, dy in self.DIRECTIONS:
                        # 提高对手活三的威胁权重
                        score -= (self._evaluate_direction(i, j, dx, dy, opponent) * 1.5) + self.DEFENSE_BONUS

        return score

    def _evaluate_direction(self, i, j, dx, dy, player):
        pattern = []
        for k in range(-4, 5):
            x, y = i + k * dx, j + k * dy
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                pattern.append(self.board[x][y])
            else:
                pattern.append(-1)

        pattern_str = ''.join(['1' if p == player else '0' if p == 0 else '2' for p in pattern])
        center_index = 4

        score = 0

        if '11111' in pattern_str:
            return self.FIVE

        if pattern_str[center_index - 4:center_index + 5] == '011110':
            return self.OPEN_FOUR

        for pos in range(0, 5):
            substr = pattern_str[pos:pos + 5]
            if substr in ['011112', '211110', '10111', '11101', '11011']:
                score += self.FOUR

        for pos in range(0, 6):
            substr = pattern_str[pos:pos + 5]
            if substr in ['001110', '011100', '010110', '011010']:
                score += self.OPEN_THREE

        for pos in range(0, 5):
            substr = pattern_str[pos:pos + 5]
            if substr in ['001112', '211100', '010112', '211010', '011012']:
                score += self.THREE

        two_count = 0
        for pos in range(0, 7):
            substr = pattern_str[pos:pos + 5]
            if substr == '001100' or substr == '011000' or substr == '000110':
                two_count += 1

        if two_count >= 2:
            score += self.DOUBLE_OPEN_TWO
        elif two_count == 1:
            score += self.OPEN_TWO

        if '01' in pattern_str:
            score += self.ONE

        return score

    def alpha_beta(self, depth, alpha, beta, maximizing_player, start_time):
        if time.time() - start_time > self.TIME_LIMIT:
            return 0, None

        if depth == 0:
            ai_score = self.evaluate_position(self.ai_player)
            human_score = self.evaluate_position(self.human_player) + self.DEFENSE_BONUS
            return ai_score - human_score * 1.5, None

        valid_moves = self.get_valid_moves()

        if not valid_moves:
            return 0, None

        sorted_moves = self._sort_moves(valid_moves, self.ai_player if maximizing_player else self.human_player, depth)

        best_move = None
        if maximizing_player:
            max_score = -float('inf')
            for move in sorted_moves:
                row, col = move
                self.board[row][col] = self.ai_player
                self._update_threat_space()

                score, _ = self.alpha_beta(depth - 1, alpha, beta, False, start_time)

                self.board[row][col] = 0
                self._update_threat_space()

                self.history_table[row][col] += 2 ** depth
                if self.AI_is_in_defense_mode():
                    self.history_table[row][col] *= 1.5

                if score > max_score:
                    max_score = score
                    best_move = move
                    if depth == self.SEARCH_DEPTH:
                        self.best_move = move
                        self.max_score = score

                alpha = max(alpha, max_score)
                if beta <= alpha:
                    if depth >= 2 and move != self.killer_moves[depth]:
                        self.killer_moves[depth] = move
                    break

            return max_score, best_move
        else:
            min_score = float('inf')
            for move in sorted_moves:
                row, col = move
                self.board[row][col] = self.human_player
                self._update_threat_space()

                score, _ = self.alpha_beta(depth - 1, alpha, beta, True, start_time)

                self.board[row][col] = 0
                self._update_threat_space()

                self.history_table[row][col] += 2 ** depth
                if self.AI_is_in_defense_mode():
                    self.history_table[row][col] *= 1.5

                if score < min_score:
                    min_score = score
                    best_move = move

                beta = min(beta, min_score)
                if beta <= alpha:
                    if depth >= 2 and move != self.killer_moves[depth]:
                        self.killer_moves[depth] = move
                    break

            return min_score, best_move

    def AI_is_in_defense_mode(self):
        opponent_score = self.evaluate_position(self.human_player)
        return opponent_score > self.OPEN_THREE * 0.8

    def _sort_moves(self, moves, player, depth=None):
        move_scores = []
        killer = self.killer_moves[depth] if depth is not None and depth <= self.MAX_DEPTH else None

        for move in moves:
            row, col = move
            score = 0

            if move == killer:
                score += 10000

            score += self.history_table[row][col]

            if self.AI_is_in_defense_mode():
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx == 0 and dy == 0:
                            continue
                        ni, nj = row + dx, col + dy
                        if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                            if self.board[ni][nj] == self.human_player:
                                score += 3000  # 提高防守加成

            center_dist = abs(row - self.board_size // 2) + abs(col - self.board_size // 2)
            score += 100 / (center_dist + 1)

            self.board[row][col] = player
            score += self.evaluate_position(player) * 0.1
            self.board[row][col] = 0

            move_scores.append((score, move))

        move_scores.sort(key=lambda x: x[0], reverse=True)
        return [move for _, move in move_scores]

    def find_best_move(self):
        if self.move_count < 4:
            opening_move = self._get_opening_move()
            if opening_move:
                return opening_move

        urgent_move = self._check_urgent_situation()
        if urgent_move:
            return urgent_move

        start_time = time.time()
        best_move = None
        best_score = -float('inf')
        depth = self.SEARCH_DEPTH

        while depth <= self.MAX_DEPTH and time.time() - start_time < self.TIME_LIMIT:
            score, move = self.alpha_beta(depth, -float('inf'), float('inf'), True, start_time)

            if move and (score > best_score or best_move is None):
                best_score = score
                best_move = move
                self.best_move = move
                self.max_score = score

            depth += 1

        if best_move:
            return best_move

        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None

        return self._fallback_strategy(valid_moves)

    def _get_opening_move(self):
        board_state = self.board.tolist()
        empty_count = np.count_nonzero(self.board == 0)

        if empty_count == self.board_size * self.board_size:
            return (self.board_size // 2, self.board_size // 2)
        elif empty_count >= (self.board_size * self.board_size) - 2:
            center = self.board_size // 2
            return random.choice([
                (center - 2, center - 2), (center + 2, center + 2),
                (center - 2, center + 2), (center + 2, center - 2)
            ])

        return None

    def _check_urgent_situation(self):
        ai_win_move = self._find_winning_move(self.ai_player)
        if ai_win_move:
            return ai_win_move

        human_win_move = self._find_winning_move(self.human_player)
        if human_win_move:
            return human_win_move

        open_four_move = self._find_pattern_move(self.human_player, self.OPEN_FOUR)
        if open_four_move:
            return open_four_move

        four_move = self._find_pattern_move(self.human_player, self.FOUR)
        if four_move:
            return four_move

        double_open_three = self._find_double_pattern(self.human_player, self.OPEN_THREE)
        if double_open_three:
            return double_open_three

        open_three_block = self._find_open_three_block()
        if open_three_block:
            return open_three_block

        ai_open_four = self._find_pattern_move(self.ai_player, self.OPEN_FOUR)
        if ai_open_four:
            return ai_open_four

        ai_double_three = self._find_double_pattern(self.ai_player, self.OPEN_THREE)
        if ai_double_three:
            return ai_double_three

        block_move = self._find_adjacent_blocking_move()
        if block_move:
            return block_move

        return None

    def _find_winning_move(self, player):
        for move in self.get_valid_moves():
            i, j = move
            self.board[i][j] = player
            if self._check_five_in_row(i, j, player):
                self.board[i][j] = 0
                return move
            self.board[i][j] = 0
        return None

    def _check_five_in_row(self, i, j, player):
        for dx, dy in self.DIRECTIONS:
            count = 1
            for step in range(1, 5):
                x, y = i + dx * step, j + dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            for step in range(1, 5):
                x, y = i - dx * step, j - dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def _find_pattern_move(self, player, pattern_score):
        target_score = pattern_score * 0.8
        for move in self.get_valid_moves():
            i, j = move
            self.board[i][j] = player
            score = self.evaluate_position(player)
            self.board[i][j] = 0

            if score >= target_score:
                return move
        return None

    def _find_double_pattern(self, player, pattern_score):
        for move in self.get_valid_moves():
            i, j = move
            self.board[i][j] = player
            score = 0
            direction_count = 0

            for dx, dy in self.DIRECTIONS:
                dir_score = self._evaluate_direction(i, j, dx, dy, player)
                if dir_score >= pattern_score * 0.8:
                    direction_count += 1
                    score += dir_score

            self.board[i][j] = 0

            if direction_count >= 2 and score >= pattern_score * 1.5:
                return move
        return None

    def _find_adjacent_blocking_move(self):
        opponent = self.human_player
        best_blocking_moves = []

        for move in self.threat_space:
            i, j = move
            adjacent_to_opponent = False
            for dx, dy in self.DIRECTIONS:
                ni, nj = i + dx, j + dy
                if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                    if self.board[ni][nj] == opponent:
                        adjacent_to_opponent = True
                        break

            if adjacent_to_opponent:
                self.board[i][j] = opponent
                threat_score = self.evaluate_position(opponent)
                self.board[i][j] = 0

                if threat_score >= self.THREE * 0.8:
                    best_blocking_moves.append((threat_score, move))

        if best_blocking_moves:
            best_blocking_moves.sort(key=lambda x: x[0], reverse=True)
            return best_blocking_moves[0][1]

        return None

    def _find_open_three_block(self):
        opponent = self.human_player
        best_block_moves = []

        for move in self.get_valid_moves():
            i, j = move
            self.board[i][j] = opponent

            is_open_three = False
            for dx, dy in self.DIRECTIONS:
                pattern = []
                for k in range(-3, 4):
                    x, y = i + k * dx, j + k * dy
                    if 0 <= x < self.board_size and 0 <= y < self.board_size:
                        pattern.append(self.board[x][y])
                    else:
                        pattern.append(-1)

                pattern_str = ''.join(['1' if p == opponent else '0' if p == 0 else '2' for p in pattern])

                # 检测更多活三变种模式
                if '01110' in pattern_str or '010110' in pattern_str or '011010' in pattern_str:
                    is_open_three = True
                    break

            self.board[i][j] = 0

            if is_open_three:
                self.board[i][j] = opponent
                threat_score = self.evaluate_position(opponent)
                self.board[i][j] = 0
                best_block_moves.append((threat_score, move))

        if best_block_moves:
            best_block_moves.sort(key=lambda x: x[0], reverse=True)
            return best_block_moves[0][1]

        return None

    def _fallback_strategy(self, valid_moves):
        center = self.board_size // 2
        center_moves = [m for m in valid_moves
                        if abs(m[0] - center) <= 3 and abs(m[1] - center) <= 3]
        if center_moves:
            return random.choice(center_moves)

        return random.choice(valid_moves) if valid_moves else None

    def make_decision(self, board_state=None):
        if board_state is not None:
            self.set_board_state(board_state)

        best_move = self.find_best_move()

        if not best_move:
            valid_moves = self.get_valid_moves()
            if valid_moves:
                best_move = random.choice(valid_moves)
            else:
                return None

        self.update_board(best_move[0], best_move[1], self.ai_player)
        return best_move

    def update_board(self, row, col, player):
        if self.is_valid_position(row, col):
            self.board[row][col] = player
            self.move_count += 1
            self._update_threat_space()
            return True
        return False

    def is_valid_position(self, row, col):
        return (0 <= row < self.board_size and
                0 <= col < self.board_size and
                self.board[row][col] == 0)

    def get_empty_positions(self):
        return [(i, j) for i in range(self.board_size)
                for j in range(self.board_size) if self.board[i][j] == 0]

    def reset_board(self):
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.move_count = 0
        self.best_move = None
        self.max_score = -float('inf')
        self.threat_space = set()
        self.history_table.fill(0)
        self.killer_moves = [None] * (self.MAX_DEPTH + 1)

    def get_ai_info(self):
        return {
            'board_size': self.board_size,
            'ai_player': self.ai_player,
            'human_player': self.human_player,
            'last_best_move': self.best_move,
            'last_max_score': self.max_score,
            'move_count': self.move_count,
            'defense_mode': self.AI_is_in_defense_mode()
        }