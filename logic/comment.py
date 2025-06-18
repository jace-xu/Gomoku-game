"""
五子棋游戏评语生成模块
使用AI API生成游戏评语和分析
"""

import json
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI


def load_env_file(env_path: str = ".env") -> None:
    """
    从.env文件加载环境变量
    
    :param env_path: .env文件路径
    """
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")


class GameCommentator:
    """使用AI API分析游戏并生成评语的五子棋游戏评论员"""
    
    def __init__(self, api_key: str = None, 
                 base_url: str = None,
                 model: str = None):
        """
        初始化评语生成器
        
        :param api_key: OpenAI API密钥（可选，如果未提供则从环境变量读取）
        :param base_url: API基础URL（可选，如果未提供则从环境变量读取）
        :param model: 要使用的模型名称（可选，如果未提供则从环境变量读取）
        """
        # 加载环境变量
        load_env_file()
        
        # 使用提供的值或回退到环境变量
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', '')
        self.base_url = base_url or os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.model = model or os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        
        if not self.api_key:
            print("Warning: No API key found. Please set DEEPSEEK_API_KEY environment variable or create .env file")
        
        self.client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """初始化OpenAI客户端"""
        try:
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                print("Cannot initialize AI client: API key not found")
                self.client = None
        except Exception as e:
            print(f"Failed to initialize AI client: {e}")
            self.client = None
    
    def read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        读取JSON文件
        
        :param file_path: JSON文件路径
        :return: 解析后的JSON数据，失败时返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def generate_comment_from_file(self, file_path: str) -> str:
        """
        从JSON文件生成评语
        
        :param file_path: 历史记录JSON文件路径
        :return: 生成的评语文本
        """
        json_data = self.read_json_file(file_path)
        if json_data is None:
            return "Unable to read game data"
        
        return self.generate_comment_from_data(json_data)
    
    def generate_comment_from_data(self, game_data: Dict[str, Any]) -> str:
        """
        从游戏数据生成评语
        
        :param game_data: 游戏数据字典
        :return: 生成的评语文本
        """
        if self.client is None:
            return "AI commentary service unavailable"
        
        try:
            # 根据游戏结果确定获胜方
            winner_info = ""
            if 'result' in game_data:
                if game_data['result'] == 1:
                    winner_info = " The human player (black pieces) WON this game."
                elif game_data['result'] == 0:
                    winner_info = " The AI player (white pieces) WON this game."
                elif game_data['result'] == 2:
                    winner_info = " This game ended in a DRAW."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a professional Gomoku player. Analyze the following game data and provide insightful commentary. Important: 1=black pieces (human player), 2=white pieces (AI player), 0=empty position. Focus on key moves and strategic plays. Give a single paragraph commentary without markdown formatting, just plain text.{winner_info} End your commentary by congratulating the winner - if human won, congratulate the player; if AI won, encourage the player to try again.不要出现ai和human的字眼，只说白棋方和黑棋方。长度控制在100词以内。 Respond in English only."
                    },
                    {
                        "role": "user", 
                        "content": json.dumps(game_data, ensure_ascii=False)
                    }
                ],
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Failed to generate commentary: {e}")
            return "Commentary generation failed, but this was an exciting game"
    
    def generate_comment(self, board_state: List[List[int]], move_history: List[List[int]], game_result: int = None) -> str:
        """
        基于棋盘状态和走棋历史生成评语
        
        :param board_state: 棋盘状态二维数组
        :param move_history: 走棋历史列表，每项为 [x, y, player]
        :param game_result: 游戏结果（0=AI获胜，1=人类获胜，2=平局）
        :return: 生成的评语文本
        """
        game_data = {
            "board": board_state,
            "moves": move_history,
            "move_count": len(move_history),
            "board_size": len(board_state) if board_state else 0
        }
        
        # 添加游戏结果信息
        if game_result is not None:
            game_data["result"] = game_result
        
        return self.generate_comment_from_data(game_data)
    
    def is_available(self) -> bool:
        """
        检查评语生成服务是否可用
        
        :return: 如果服务可用返回True，否则返回False
        """
        return self.client is not None and bool(self.api_key)
    
    def get_fallback_comment(self, move_count: int = 0) -> str:
        """
        获取备用评语（当AI服务不可用时使用）
        
        :param move_count: 已下棋步数
        :return: 备用评语文本
        """
        fallback_comments = [
            "Excellent game!",
            "Both players showed great skill, intense battle",
            "Exciting offensive and defensive plays, worth reviewing",
            "Every move was filled with wisdom",
            "A high-quality Gomoku game"
        ]
        
        if move_count > 50:
            return "A long and exciting game where both players demonstrated exceptional skill"
        elif move_count < 20:
            return "A quick and decisive battle with excellent plays"
        else:
            import random
            return random.choice(fallback_comments)


# 创建默认实例以保持向后兼容性
_default_commentator = None

def get_default_commentator() -> GameCommentator:
    """获取默认评论员实例"""
    global _default_commentator
    if _default_commentator is None:
        _default_commentator = GameCommentator()
    return _default_commentator

def generate_comment(board_state: List[List[int]], move_history: List[List[int]], game_result: int = None) -> str:
    """
    便利函数：生成游戏评语
    保持与现有接口的兼容性
    
    :param board_state: 棋盘状态
    :param move_history: 走棋历史
    :param game_result: 游戏结果（0=AI获胜，1=人类获胜，2=平局）
    :return: 评语文本
    """
    commentator = get_default_commentator()
    return commentator.generate_comment(board_state, move_history, game_result)

# 为了兼容性，保留原始函数接口
def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """向后兼容的文件读取函数"""
    commentator = get_default_commentator()
    return commentator.read_json_file(file_path)
