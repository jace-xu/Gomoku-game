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
    
    def __init__(self, board_size=15, ai_player=2, human_player=1):
        """
        初始化AI决策器
        
        参数:
            board_size (int): 棋盘大小，默认15
            ai_player (int): AI玩家编号(1=黑棋, 2=白棋)，默认2
            human_player (int): 人类玩家编号(1=黑棋, 2=白棋)，默认1
        """
        if ai_player == human_player:
            raise ValueError("AI玩家和人类玩家编号不能相同")
        if ai_player not in [1, 2] or human_player not in [1, 2]:
            raise ValueError("玩家编号必须是1或2")
        
        self.board_size = board_size
        self.ai_player = ai_player
        self.human_player = human_player
        
        # 实例变量：当前棋盘状态
        self.board = np.zeros((board_size, board_size), dtype=int)
        
        # AI决策结果
        self.best_move = None
        self.max_score = -float('inf')
    
    def set_board_state(self, board):
        """
        设置当前棋盘状态
        
        参数:
            board (numpy.ndarray or list): 棋盘状态
        """
        if isinstance(board, list):
            board = np.array(board)
        
        if not isinstance(board, np.ndarray):
            raise TypeError("棋盘状态必须是numpy数组或二维列表")
        
        if board.shape != (self.board_size, self.board_size):
            raise ValueError(f"棋盘状态必须是大小为{self.board_size}x{self.board_size}的数组")
        
        self.board = board.copy().astype(int)
    
    def get_board_state(self):
        """
        获取当前棋盘状态
        
        返回:
            numpy.ndarray: 当前棋盘状态的副本
        """
        return self.board.copy()
    
    def is_valid_position(self, row, col):
        """
        检查位置是否有效且为空
        
        参数:
            row (int): 行坐标
            col (int): 列坐标
        
        返回:
            bool: 位置是否有效且为空
        """
        return (0 <= row < self.board_size and 
                0 <= col < self.board_size and 
                self.board[row][col] == 0)
    
    def get_empty_positions(self):
        """
        获取所有空位置
        
        返回:
            list: 空位置坐标列表 [(row, col), ...]
        """
        empty_positions = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    empty_positions.append((row, col))
        return empty_positions
    
    def evaluate_pattern(self, pattern):
        """评估给定棋型的分数"""
        for i, c_pattern in enumerate(self.CDATA):
            if pattern == c_pattern:
                return (len(self.CDATA) - i) * 10
        return 0
    
    def evaluate_position(self, row, col, player):
        """
        评估在指定位置落子的分数
        
        参数:
            row (int): 行坐标
            col (int): 列坐标
            player (int): 玩家编号
        
        返回:
            int: 位置评分
        """
        if not self.is_valid_position(row, col):
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
                    pattern.append(self.human_player if player == self.ai_player else self.ai_player)
            
            score = self.evaluate_pattern(pattern)
            if player == self.ai_player:
                total_score += score * 1.2
            else:
                total_score += score
        
        return total_score
    
    def find_best_move(self):
        """
        寻找最佳落子位置
        
        返回:
            tuple or None: 最佳位置坐标(row, col)，如果没有找到则返回None
        """
        self.max_score = -float('inf')
        self.best_move = None
        
        empty_positions = self.get_empty_positions()
        if not empty_positions:
            return None
        
        for row, col in empty_positions:
            ai_score = self.evaluate_position(row, col, self.ai_player)
            human_score = self.evaluate_position(row, col, self.human_player)
            
            score = ai_score + human_score * 0.8
            
            # 中心位置加分
            center_bonus = 1.0 - (abs(row - self.board_size//2) + abs(col - self.board_size//2)) / (self.board_size * 2)
            score *= (1.0 + center_bonus * 0.2)
            
            if score > self.max_score:
                self.max_score = score
                self.best_move = (row, col)
        
        return self.best_move
    
    def make_decision(self, board_state=None):
        """
        执行AI决策，返回落子位置
        
        参数:
            board_state (numpy.ndarray or list, optional): 棋盘状态，如果提供则更新内部状态
        
        返回:
            tuple or None: 最佳落子位置坐标(row, col)，如果无有效位置返回None
        """
        if board_state is not None:
            self.set_board_state(board_state)
        
        best_move = self.find_best_move()
        
        # 如果找不到最佳位置，随机选择一个空位
        if best_move is None or self.max_score <= 0:
            empty_positions = self.get_empty_positions()
            if empty_positions:
                best_move = random.choice(empty_positions)
        
        return best_move
    
    def update_board(self, row, col, player):
        """
        更新棋盘状态
        
        参数:
            row (int): 行坐标
            col (int): 列坐标
            player (int): 玩家编号
        
        返回:
            bool: 是否成功更新
        """
        if self.is_valid_position(row, col):
            self.board[row][col] = player
            return True
        return False
    
    def reset_board(self):
        """重置棋盘状态"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.best_move = None
        self.max_score = -float('inf')
    
    def get_ai_info(self):
        """
        获取AI信息
        
        返回:
            dict: AI配置信息
        """
        return {
            'board_size': self.board_size,
            'ai_player': self.ai_player,
            'human_player': self.human_player,
            'last_best_move': self.best_move,
            'last_max_score': self.max_score
        }