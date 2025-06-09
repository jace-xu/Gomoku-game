class BoardState:
    def __init__(self, size=15, ai_player=2, human_player=1, first_player=1):
        """
        初始化棋盘状态对象。
        :param表示参数

        :param size: 棋盘边长，默认15（15x15）
        :param ai_player: AI执子编号（1=黑，2=白），默认2（白）
        :param human_player: 人类执子编号（1=黑，2=白），默认1（黑）
        :param first_player: 首手玩家编号（1或2），默认1（黑先）
        """
        self.size = size                       # 棋盘边长
        self.ai_player = ai_player             # AI执子
        self.human_player = human_player       # 人类执子
        self.board = None                      # 棋盘二维数组，后续在reset中初始化
        self.move_history = None               # 保存落子历史，便于悔棋或复盘
        self.current_player = None             # 记录当前轮到哪方
        self.winner = None                     # 胜者编号，None表示未分胜负
        self.reset(first_player)               # 初始化棋盘和其它状态

    def reset(self, first_player=1):
        """
        重置棋盘和对局状态。可指定先手玩家。

        :param first_player: 先手玩家编号（1或2）
        """
        self.board = [[0]*self.size for _ in range(self.size)]  # 0表示空，1/2分别代表黑/白
        self.move_history = []          # 清空历史记录
        self.current_player = first_player  # 重新设定先手
        self.winner = None              # 清空胜负标记

    def move(self, x, y):
        """
        在(x, y)坐标为当前玩家落子，并自动切换到对方回合。如果落子后分出胜负，则设置winner。

        :param x: 横坐标（列号，0开始）
        :param y: 纵坐标（行号，0开始）
        """
        # 仅在目标格为空且未分胜负时允许落子
        if self.board[y][x] == 0 and not self.winner:
            self.board[y][x] = self.current_player
            self.move_history.append((x, y, self.current_player))  # 记录落子历史
            if self.check_win(x, y, self.current_player):          # 判断胜负
                self.winner = self.current_player
            self.current_player = 3 - self.current_player          # 切换玩家（1<->2）

    def check_win(self, x, y, player):
        """
        检查以(x, y)为落点，player是否形成五子连珠。

        :param x: 落子横坐标
        :param y: 落子纵坐标
        :param player: 检查的玩家编号（1或2）
        :return: True if 胜负已分，否则False
        """
        # 四个方向：→、↓、↘、↙
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1  # 本点计1
            # 检查两个方向（正和负）
            for d in (1, -1):
                for i in range(1, 5):  # 最远只需检查4格
                    nx, ny = x + dx*i*d, y + dy*i*d
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
        悔棋：撤销最后一步操作，并恢复上一方执棋。
        """
        if self.move_history:
            x, y, player = self.move_history.pop()
            self.board[y][x] = 0
            self.current_player = player     # 恢复到撤销前的玩家
            self.winner = None              # 撤销后需重新判断胜负（可扩展）