"""
Gomoku Game Commentary Generation Module
Uses AI API to generate game commentary and analysis
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI


class GameCommentator:
    """Gomoku game commentator that uses AI API to analyze games and generate commentary"""
    
    def __init__(self, api_key: str = "sk-3be5fd048318406f9e9bd47a376aea71", 
                 base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat"):
        """
        Initialize commentary generator
        
        :param api_key: OpenAI API key
        :param base_url: API base URL
        :param model: Model name to use
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception as e:
            print(f"Failed to initialize AI client: {e}")
            self.client = None
    
    def read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Read JSON file
        
        :param file_path: JSON file path
        :return: Parsed JSON data, None if failed
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
        Generate commentary from JSON file
        
        :param file_path: History record JSON file path
        :return: Generated commentary text
        """
        json_data = self.read_json_file(file_path)
        if json_data is None:
            return "Unable to read game data"
        
        return self.generate_comment_from_data(json_data)
    
    def generate_comment_from_data(self, game_data: Dict[str, Any]) -> str:
        """
        Generate commentary from game data
        
        :param game_data: Game data dictionary
        :return: Generated commentary text
        """
        if self.client is None:
            return "AI commentary service unavailable"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional Gomoku player. You need to analyze the following JSON game data and provide insightful commentary. 读取最新的游戏记录，引用一些棋子的位置坐标来说明你的观点。文件中1代表的是黑棋，也就是玩家；2代表的是白棋，也就是ai。0代表的空位。评价要生动易懂。给出一个简单的，只有一段的评价，不要分条，也不要分自然段，也不要任何markdown语言，给我纯文字。评价完了加上一句，如果玩家获胜就恭喜player，如果ai赢了，就鼓励player不要气馁，再来一局。Respond in English only."
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
    
    def generate_comment(self, board_state: List[List[int]], move_history: List[List[int]]) -> str:
        """
        Generate commentary based on board state and move history
        
        :param board_state: Board state 2D array
        :param move_history: Move history list, each item is [x, y, player]
        :return: Generated commentary text
        """
        game_data = {
            "board": board_state,
            "moves": move_history,
            "move_count": len(move_history),
            "board_size": len(board_state) if board_state else 0
        }
        
        return self.generate_comment_from_data(game_data)
    
    def is_available(self) -> bool:
        """
        Check if commentary generation service is available
        
        :return: True if service is available, False otherwise
        """
        return self.client is not None
    
    def get_fallback_comment(self, move_count: int = 0) -> str:
        """
        Get fallback commentary (used when AI service is unavailable)
        
        :param move_count: Number of moves played
        :return: Fallback commentary text
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


# Create default instance to maintain backward compatibility
_default_commentator = None

def get_default_commentator() -> GameCommentator:
    """Get default commentator instance"""
    global _default_commentator
    if _default_commentator is None:
        _default_commentator = GameCommentator()
    return _default_commentator

def generate_comment(board_state: List[List[int]], move_history: List[List[int]]) -> str:
    """
    Convenience function: generate game commentary
    Maintains compatibility with existing interface
    
    :param board_state: Board state
    :param move_history: Move history
    :return: Commentary text
    """
    commentator = get_default_commentator()
    return commentator.generate_comment(board_state, move_history)

# For compatibility, keep original function interface
def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Backward compatible file reading function"""
    commentator = get_default_commentator()
    return commentator.read_json_file(file_path)
