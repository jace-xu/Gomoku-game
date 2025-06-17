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
                        "content": f"You are a professional Gomoku player. Analyze the following game data and provide insightful commentary. Important: 1=black pieces (human player), 2=white pieces (AI player), 0=empty position. Focus on key moves and strategic plays. Give a single paragraph commentary without markdown formatting, just plain text.{winner_info} End your commentary by congratulating the winner - if human won, congratulate the player; if AI won, encourage the player to try again.不要出现ai和human的字眼，只说白棋方和黑棋方。 Respond in English only."
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
        Generate commentary based on board state and move history
        
        :param board_state: Board state 2D array
        :param move_history: Move history list, each item is [x, y, player]
        :param game_result: Game result (0=AI win, 1=human win, 2=draw)
        :return: Generated commentary text
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

def generate_comment(board_state: List[List[int]], move_history: List[List[int]], game_result: int = None) -> str:
    """
    Convenience function: generate game commentary
    Maintains compatibility with existing interface
    
    :param board_state: Board state
    :param move_history: Move history
    :param game_result: Game result (0=AI win, 1=human win, 2=draw)
    :return: Commentary text
    """
    commentator = get_default_commentator()
    return commentator.generate_comment(board_state, move_history, game_result)

# For compatibility, keep original function interface
def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Backward compatible file reading function"""
    commentator = get_default_commentator()
    return commentator.read_json_file(file_path)
