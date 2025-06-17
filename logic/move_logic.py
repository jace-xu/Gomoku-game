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
        if self.difficulty_level == 1:  # Easy - 完全随机
            self.SEARCH_DEPTH = 0  # 不使用搜索
            self.DEFENSE_WEIGHT = 0.1  # 几乎不防守
            self.PROXIMITY_WEIGHT = 50  # 很低的邻近权重
            self.COMBO_THREAT_BONUS = 1000  # 大幅降低威胁检测
            self.WINNING_PRIORITY = 10000  # 很低的获胜优先级
            self.use_random_strategy = True  # 启用完全随机策略
            self.random_probability = 0.95  # 95%概率完全随机
        elif self.difficulty_level == 2:  # Normal - 中等智能
            self.SEARCH_DEPTH = 2
            self.DEFENSE_WEIGHT = 4.0
            self.PROXIMITY_WEIGHT = 3000
            self.COMBO_THREAT_BONUS = 800000
            self.WINNING_PRIORITY = 10000000
            self.use_random_strategy = False
            self.random_probability = 0.0
        elif self.difficulty_level == 3:  # Hard - 超强AI
            self.SEARCH_DEPTH = 4  # 增加搜索深度
            self.DEFENSE_WEIGHT = 10.0  # 大幅提高防守权重
            self.PROXIMITY_WEIGHT = 8000  # 提高位置价值
            self.COMBO_THREAT_BONUS = 2000000  # 更强的威胁检测
            self.WINNING_PRIORITY = 50000000  # 最高获胜优先级
            self.use_random_strategy = False
            self.random_probability = 0.0
            # Hard模式专用设置
            self.enable_deep_analysis = True
            self.enable_killer_moves = True
            self.enable_advanced_patterns = True
        
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
        try:
            print(f"AI决策开始，当前难度: {self.difficulty_level}")
            
            # Easy难度：主要使用随机策略
            if self.difficulty_level == 1:
                return self._make_easy_move()
            
            # Hard难度：使用强策略
            elif self.difficulty_level == 3:
                return self._make_hard_move()
            
            # Normal难度：使用平衡策略
            else:
                return self._make_normal_move()
                
        except Exception as e:
            print(f"AI决策异常: {e}")
            # 异常时根据难度选择备用策略
            if self.difficulty_level == 1:
                return self._pure_random_move()
            else:
                return self._make_safe_move()

    def _make_easy_move(self):
        """Easy难度：主要随机，偶尔智能"""
        try:
            print("Easy AI开始决策")
            valid_moves = self.get_valid_moves()
            if not valid_moves:
                return None
            
            # 95%概率完全随机
            if random.random() < 0.95:
                selected = random.choice(valid_moves)
                print(f"Easy AI随机选择: {selected}")
                return selected
            
            # 5%概率稍微智能一点
            # 检查能否获胜
            for move in valid_moves[:5]:
                row, col = move
                if self._is_winning_move_at_position(row, col, self.ai_player):
                    print("Easy AI偶然发现获胜机会")
                    return (row, col)
            
            # 检查是否必须防守
            for move in valid_moves[:5]:
                row, col = move
                if self._is_winning_move_at_position(row, col, self.human_player):
                    print("Easy AI偶然执行防守")
                    return (row, col)
            
            # 否则随机选择
            selected = random.choice(valid_moves)
            print(f"Easy AI随机选择: {selected}")
            return selected
            
        except Exception as e:
            print(f"Easy AI异常: {e}")
            return self._pure_random_move()

    def _make_normal_move(self):
        """Normal难度：平衡的策略"""
        try:
            print("Normal AI开始决策")
            
            # 1. 检查获胜机会
            winning_move = self._find_winning_move_simple()
            if winning_move:
                print("Normal AI发现获胜机会")
                return winning_move
            
            # 2. 检查防守需要
            blocking_move = self._find_critical_blocking_move()
            if blocking_move:
                print("Normal AI执行防守")
                return blocking_move
            
            # 3. 使用简化搜索
            try:
                _, move = self.alpha_beta(min(2, self.SEARCH_DEPTH), -float('inf'), float('inf'), True)
                if move and self._is_position_valid(move):
                    print("Normal AI使用搜索决策")
                    return move
            except Exception as search_error:
                print(f"Normal AI搜索异常: {search_error}")
            
            # 4. 选择最佳可用位置
            valid_moves = [move for move in self.get_valid_moves() if self._is_position_valid(move)]
            if valid_moves:
                try:
                    sorted_moves = self._sort_moves(valid_moves[:10], self.ai_player)
                    if sorted_moves:
                        print("Normal AI选择高分位置")
                        return sorted_moves[0]
                except Exception as sort_error:
                    print(f"排序异常: {sort_error}")
                
                # 如果排序失败，随机选择
                print("Normal AI随机选择")
                return random.choice(valid_moves[:5])
            
            return None
            
        except Exception as e:
            print(f"Normal AI异常: {e}")
            return self._make_random_move()

    def _make_hard_move(self):
        """Hard难度：强AI策略（重新设计，确保稳定）"""
        try:
            print("Hard AI开始决策")
            
            # 1. 最高优先级：检查AI能否获胜
            winning_move = self._find_winning_move_simple()
            if winning_move:
                print("Hard AI发现获胜机会！")
                return winning_move

            # 2. 第二优先级：阻止对手获胜
            blocking_move = self._find_critical_blocking_move()
            if blocking_move:
                print("Hard AI执行关键防守")
                return blocking_move

            # 3. 第三优先级：创造威胁
            threat_move = self._find_threat_creating_move()
            if threat_move:
                print("Hard AI创造威胁")
                return threat_move

            # 4. 第四优先级：阻止对手威胁
            defense_move = self._find_defense_move()
            if defense_move:
                print("Hard AI防守威胁")
                return defense_move

            # 5. 使用深度搜索
            try:
                _, move = self.alpha_beta(self.SEARCH_DEPTH, -float('inf'), float('inf'), True)
                if move and self._is_position_valid(move):
                    print("Hard AI使用搜索决策")
                    return move
            except Exception as search_error:
                print(f"搜索异常: {search_error}")

            # 6. 战略位置选择
            strategic_move = self._choose_strategic_position()
            if strategic_move:
                print("Hard AI选择战略位置")
                return strategic_move

            # 最后备选
            safe_move = self._make_safe_move()
            print("Hard AI使用安全策略")
            return safe_move

        except Exception as e:
            print(f"Hard AI异常: {e}")
            # 降级到普通AI
            return self._make_normal_move()

    def _make_random_move(self):
        """简单的随机移动"""
        try:
            valid_moves = self.get_valid_moves()
            if valid_moves:
                return random.choice(valid_moves)
            return None
        except Exception as e:
            print(f"随机移动异常: {e}")
            return None

    def _find_winning_move_simple(self):
        """简单版本的获胜检测"""
        valid_moves = self.get_valid_moves()
        
        for move in valid_moves[:10]:  # 只检查前10个位置，提高效率
            row, col = move
            if self._is_winning_move_at_position(row, col, self.ai_player):
                return (row, col)
        
        return None

    def _is_winning_move_at_position(self, row, col, player):
        """检查在指定位置落子是否能获胜"""
        # 临时放置棋子
        self.board[row][col] = player
        
        # 检查四个方向
        for dx, dy in self.DIRECTIONS:
            count = 1  # 包含当前位置
            
            # 正方向计数
            for i in range(1, 5):
                x, y = row + i * dx, col + i * dy
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            
            # 负方向计数
            for i in range(1, 5):
                x, y = row - i * dx, col - i * dy
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
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

    def _find_critical_blocking_move(self):
        """寻找关键阻挡位置"""
        valid_moves = self.get_valid_moves()
        
        # 检查对手的直接获胜威胁
        for move in valid_moves:
            row, col = move
            if self._is_winning_move_at_position(row, col, self.human_player):
                return (row, col)
        
        return None

    def _find_threat_creating_move(self):
        """寻找能创造威胁的位置"""
        valid_moves = self.get_valid_moves()
        best_move = None
        max_threat = 0
        
        for move in valid_moves[:8]:  # 只检查前8个位置
            if not self._is_position_valid(move):
                continue
                
            row, col = move
            threat_score = self._count_simple_threats(row, col, self.ai_player)
            
            if threat_score > max_threat:
                max_threat = threat_score
                best_move = move
        
        # 只有威胁足够大时才返回
        if max_threat >= 3:
            return best_move
        
        return None

    def _find_defense_move(self):
        """寻找防守位置"""
        valid_moves = self.get_valid_moves()
        best_move = None
        max_defense_score = 0
        
        for move in valid_moves:
            row, col = move
            defense_score = self._calculate_threat_score(row, col, self.human_player)
            
            if defense_score > max_defense_score:
                max_defense_score = defense_score
                best_move = move
        
        # 只有威胁足够大时才防守
        if max_defense_score >= 2:
            return best_move
        
        return None

    def _count_simple_threats(self, row, col, player):
        """计算简单威胁数量"""
        # 临时放置棋子
        self.board[row][col] = player
        
        threat_count = 0
        
        for dx, dy in self.DIRECTIONS:
            count = 1  # 包含当前位置
            
            # 正方向计数
            for i in range(1, 5):
                x, y = row + i * dx, col + i * dy
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            
            # 负方向计数
            for i in range(1, 5):
                x, y = row - i * dx, col - i * dy
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            
            # 根据连子数量计算威胁
            if count >= 4:
                threat_count += 10  # 四连是大威胁
            elif count >= 3:
                threat_count += 3   # 三连需要关注
            elif count >= 2:
                threat_count += 1   # 二连稍微留意
        
        # 恢复棋盘
        self.board[row][col] = 0
        
        return threat_count

    def _calculate_threat_score(self, row, col, player):
        """计算威胁分数"""
        # 临时放置棋子
        self.board[row][col] = player
        
        total_score = 0
        
        for dx, dy in self.DIRECTIONS:
            count = 1  # 包含当前位置
            
            # 正方向计数
            for i in range(1, 5):
                x, y = row + i * dx, col + i * dy
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            
            # 负方向计数
            for i in range(1, 5):
                x, y = row - i * dx, col - i * dy
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                    count += 1
                else:
                    break
            
            # 根据连子数量评分
            if count >= 4:
                total_score += 20  # 四连非常危险
            elif count >= 3:
                total_score += 5   # 三连需要关注
            elif count >= 2:
                total_score += 1   # 二连稍微留意
        
        # 恢复棋盘
        self.board[row][col] = 0
        
        return total_score

    def _choose_strategic_position(self):
        """选择战略位置"""
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None
        
        # 优先选择中心附近且靠近已有棋子的位置
        center = self.board_size // 2
        best_move = None
        best_score = -1
        
        for move in valid_moves:
            row, col = move
            
            # 计算到中心的距离（距离越近越好）
            distance_to_center = abs(row - center) + abs(col - center)
            center_score = max(0, 8 - distance_to_center)
            
            # 计算邻近棋子数量（有邻居更好）
            neighbor_count = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    x, y = row + dx, col + dy
                    if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] != 0:
                        neighbor_count += 1
            
            # 综合评分
            total_score = center_score + neighbor_count * 2
            
            if total_score > best_score:
                best_score = total_score
                best_move = move
        
        return best_move

    def _make_safe_move(self):
        """安全移动（备用策略）"""
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None
        
        # 优先选择中心附近的位置
        center = self.board_size // 2
        best_move = None
        min_distance = float('inf')
        
        for move in valid_moves:
            row, col = move
            distance = abs(row - center) + abs(col - center)
            if distance < min_distance:
                min_distance = distance
                best_move = move
        
        return best_move

    def _pure_random_move(self):
        """纯随机移动"""
        try:
            valid_moves = self.get_valid_moves()
            if valid_moves:
                return random.choice(valid_moves)
            return None
        except Exception as e:
            print(f"纯随机移动异常: {e}")
            return None

    def _is_position_valid(self, move):
        """检查移动是否有效"""
        if move is None:
            return False
        
        try:
            row, col = move
            return (0 <= row < self.board_size and 
                    0 <= col < self.board_size and 
                    self.board[row][col] == 0)
        except (TypeError, ValueError, IndexError):
            return False

    def _sort_moves(self, moves, player):
        """对移动进行排序，优先选择更有价值的位置"""
        if not moves:
            return []
        
        move_scores = []
        
        for move in moves:
            row, col = move
            # 临时放置棋子
            self.board[row][col] = player
            
            # 基础位置评估
            score = self.evaluate_position()
            
            # 额外的位置价值评估
            proximity_bonus = self._calculate_proximity_bonus(row, col)
            strategic_bonus = self._calculate_strategic_bonus(row, col, player)
            
            total_score = score + proximity_bonus + strategic_bonus
            
            # 恢复棋盘
            self.board[row][col] = 0
            
            move_scores.append((total_score, move))
        
        # 按分数降序排序
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in move_scores]

    def _calculate_proximity_bonus(self, row, col):
        """计算位置的邻近奖励"""
        bonus = 0
        center = self.board_size // 2
        
        # 中心位置奖励
        distance_to_center = abs(row - center) + abs(col - center)
        bonus += max(0, (center - distance_to_center)) * 10
        
        # 邻近已有棋子的奖励
        neighbor_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if (0 <= nr < self.board_size and 0 <= nc < self.board_size and 
                    self.board[nr][nc] != 0):
                    neighbor_count += 1
        
        bonus += neighbor_count * 50
        return bonus

    def _calculate_strategic_bonus(self, row, col, player):
        """计算战略位置奖励"""
        bonus = 0
        
        # 检查该位置是否能形成威胁
        for dx, dy in self.DIRECTIONS:
            line_strength = self._evaluate_line_strength(row, col, dx, dy, player)
            bonus += line_strength * 20
        
        return bonus

    def _evaluate_line_strength(self, row, col, dx, dy, player):
        """评估在某个方向上的连线强度"""
        count = 1  # 包含当前位置
        
        # 正方向计数
        for i in range(1, 5):
            x, y = row + i * dx, col + i * dy
            if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                count += 1
            else:
                break
        
        # 负方向计数
        for i in range(1, 5):
            x, y = row - i * dx, col - i * dy
            if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == player:
                count += 1
            else:
                break
        
        return count

    def alpha_beta(self, depth, alpha, beta, maximizing_player):
        """Alpha-Beta剪枝搜索"""
        if depth == 0:
            return self.evaluate_position(), None

        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return 0, None

        # 限制搜索分支数以提高性能
        max_branches = min(8, len(valid_moves))

        if maximizing_player:
            max_eval = -float('inf')
            best_move = None
            
            # 安全地获取排序后的移动
            try:
                sorted_moves = self._sort_moves(valid_moves, self.ai_player)[:max_branches]
            except Exception:
                sorted_moves = valid_moves[:max_branches]
            
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
                    break  # Beta剪枝
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            
            # 安全地获取排序后的移动
            try:
                sorted_moves = self._sort_moves(valid_moves, self.human_player)[:max_branches]
            except Exception:
                sorted_moves = valid_moves[:max_branches]
            
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
                    break  # Alpha剪枝
            
            return min_eval, best_move

    def make_decision(self, board_state=None):
        """AI决策入口方法"""
        if board_state is not None:
            self.set_board_state(board_state)
        return self.find_best_move()

    def update_board(self, row, col, player):
        """更新棋盘状态"""
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == 0:
            self.board[row][col] = player
            self._update_threat_space()
            return True
        return False

    def is_valid_position(self, row, col):
        """检查位置是否有效"""
        return 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == 0

    def get_empty_positions(self):
        """获取所有空位置"""
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