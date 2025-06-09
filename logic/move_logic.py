import numpy as np
import random

class GomokuAI:
    """五子棋AI决策模块，可独立使用或集成到游戏环境中"""
    
    # 类变量：棋型模式库，用于评估棋盘局势
    CDATA = [
        [1, 3, 0, 0, 0], [0, 1, 3, 0, 0], [0, 0, 1, 3, 0], [0, 0, 0, 1, 3], [0, 0, 0, 3, 1],
        [2, 3, 0, 0, 0], [0, 2, 3, 0, 0], [0, 0, 2, 3, 0], [0, 0, 0, 2, 3], [0, 0, 0, 3, 2],
        [0, 1, 3, 1, 0], [1, 1, 3, 0, 0], [0, 0, 3, 1, 1],
        [2, 2, 3, 0, 0], [0, 0, 3, 2, 2], [0, 2, 3, 2, 0],
        [1, 1, 1, 3, 0], [0, 3, 1, 1, 1], [1, 1, 3, 1, 0], [1, 3, 1, 1, 0],
        [2, 2, 0, 3, 2], [2, 3, 0, 2, 2], [0, 3, 2, 2, 2], [2, 2, 3, 2, 0],
        [2, 3, 2, 2, 0], [0, 2, 3, 2, 2], [0, 2, 2, 3, 2], [2, 2, 2, 3, 0], [3, 2, 2, 2, 0],
        [1, 1, 1, 1, 3], [3, 1, 1, 1, 1], [1, 1, 1, 3, 1], [1, 3, 1, 1, 1], [1, 1, 3, 1, 1],
        [2, 2, 2, 2, 3], [3, 2, 2, 2, 2], [2, 2, 3, 2, 2], [2, 3, 2, 2, 2], [2, 2, 2, 3, 2]
    ]
    
    def __init__(self, board_size=15, ai_player=2):
        """
        初始化AI决策器
        
        参数:
            board_size: 棋盘大小
            ai_player: AI玩家编号(1=黑棋, 2=白棋)
        """
        self.board_size = board_size
        self.ai_player = ai_player
        self.human_player = 1 if ai_player == 2 else 2
        
        # 实例变量：当前棋盘状态
        self.board = np.zeros((board_size, board_size), dtype=int)
        
        # AI决策结果
        self.best_move = None
        self.max_score = -float('inf')
    
    def set_board_state(self, board):
        """设置当前棋盘状态"""
        if isinstance(board, np.ndarray) and board.shape == (self.board_size, self.board_size):
            self.board = board.copy()
        else:
            raise ValueError(f"棋盘状态必须是大小为{self.board_size}x{self.board_size}的numpy数组")
    
    def evaluate_pattern(self, pattern):
        """评估给定棋型的分数"""
        for i, c_pattern in enumerate(self.CDATA):
            if pattern == c_pattern:
                # 棋型越靠后，优先级越高
                return (len(self.CDATA) - i) * 10
        return 0
    
    def evaluate_position(self, row, col, player):
        """评估在指定位置落子的分数"""
        if self.board[row][col] != 0:
            return 0
        
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        total_score = 0
        
        for dx, dy in directions:
            pattern = []
            for i in range(-2, 3):
                r = row + i * dx
                c = col + i * dy
                if 0 <= r < self.board_size and 0 <= c < self.board_size:
                    pattern.append(self.board[r][c] if (r, c) != (row, col) else player)
                else:
                    # 边界外视为对方棋子
                    pattern.append(self.human_player if player == self.ai_player else self.ai_player)
            
            # 评估棋型分数
            score = self.evaluate_pattern(pattern)
            # 进攻和防守的权重可以不同
            if player == self.ai_player:
                total_score += score * 1.2  # 进攻稍重
            else:
                total_score += score
        
        return total_score
    
    def find_best_move(self):
        """寻找最佳落子位置"""
        self.max_score = -float('inf')
        self.best_move = None
        
        # 遍历棋盘上所有空位
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    # 评估AI在此位置落子的分数
                    ai_score = self.evaluate_position(row, col, self.ai_player)
                    
                    # 评估人类在此位置落子的分数（防守）
                    human_score = self.evaluate_position(row, col, self.human_player)
                    
                    # 综合得分 = 进攻得分 + 防守得分
                    score = ai_score + human_score * 0.8  # 防守稍轻
                    
                    # 优先选择中间位置
                    center_bonus = 1.0 - (abs(row - self.board_size//2) + abs(col - self.board_size//2)) / (self.board_size * 2)
                    score *= (1.0 + center_bonus * 0.2)  # 中心位置额外加分
                    
                    # 更新最佳位置
                    if score > self.max_score:
                        self.max_score = score
                        self.best_move = (row, col)
        
        return self.best_move
    
    def make_decision(self):
        """
        执行AI决策，返回落子位置
        
        返回:
            (row, col): 最佳落子位置坐标，或None(无有效位置)
        """
        best_move = self.find_best_move()
        
        # 如果找不到最佳位置，随机选择一个空位
        if best_move is None or self.max_score <= 0:
            empty_positions = np.argwhere(self.board == 0)
            if len(empty_positions) > 0:
                best_move = tuple(empty_positions[random.randint(0, len(empty_positions)-1)])
        
        return best_move
    
    def update_board(self, row, col, player):
        """更新棋盘状态"""
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == 0:
            self.board[row][col] = player
            return True
        return False    