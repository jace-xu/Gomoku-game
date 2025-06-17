import pygame
import os
import time
from typing import List, Optional

class AnimationPlayer:
    """逐帧动画播放器"""
    
    def __init__(self, screen: pygame.Surface):
        """
        初始化动画播放器
        
        :param screen: pygame显示表面
        """
        self.screen = screen
        self.original_title = pygame.display.get_caption()[0]
        
        # 动画路径
        self.victory_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "animation-v")
        self.defeat_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "animation-d")
        
        # 动画设置
        self.frame_delay = 80  # 每帧显示时间（毫秒）
        self.background_color = (0, 0, 0)  # 黑色背景
        
    def _load_animation_frames(self, animation_path: str) -> List[pygame.Surface]:
        """
        加载动画帧
        
        :param animation_path: 动画文件夹路径
        :return: 动画帧列表
        """
        frames = []
        
        if not os.path.exists(animation_path):
            print(f"动画路径不存在: {animation_path}")
            return frames
        
        try:
            # 获取所有图片文件并排序
            files = [f for f in os.listdir(animation_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            files.sort()  # 确保按文件名顺序播放
            
            print(f"找到 {len(files)} 个动画帧文件")
            
            # 加载每一帧
            for filename in files:
                file_path = os.path.join(animation_path, filename)
                try:
                    frame = pygame.image.load(file_path).convert_alpha()
                    # 缩放到适合屏幕大小
                    screen_width, screen_height = self.screen.get_size()
                    frame = pygame.transform.scale(frame, (screen_width, screen_height))
                    frames.append(frame)
                    print(f"加载动画帧: {filename}")
                except pygame.error as e:
                    print(f"加载帧失败 {filename}: {e}")
                    
        except Exception as e:
            print(f"加载动画帧异常: {e}")
            
        return frames
    
    def play_animation(self, animation_type: str) -> bool:
        """
        播放指定类型的动画
        
        :param animation_type: 动画类型 ('victory' 或 'defeat')
        :return: 是否成功播放
        """
        # 确定动画路径
        if animation_type == 'victory':
            animation_path = self.victory_path
            window_title = "Victory!"
        elif animation_type == 'defeat':
            animation_path = self.defeat_path
            window_title = "Defeat!"
        else:
            print(f"未知的动画类型: {animation_type}")
            return False
        
        # 加载动画帧
        frames = self._load_animation_frames(animation_path)
        if not frames:
            print(f"没有找到动画帧，跳过动画播放")
            return False
        
        # 临时更改窗口标题
        pygame.display.set_caption(window_title)
        
        # 播放动画
        try:
            clock = pygame.time.Clock()
            animation_running = True
            frame_index = 0
            last_frame_time = pygame.time.get_ticks()
            
            print(f"开始播放{animation_type}动画，共{len(frames)}帧")
            
            while animation_running and frame_index < len(frames):
                current_time = pygame.time.get_ticks()
                
                # 处理事件（允许ESC键跳过动画）
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        animation_running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            animation_running = False
                        elif event.key == pygame.K_SPACE:
                            animation_running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        animation_running = False
                
                # 检查是否需要切换到下一帧
                if current_time - last_frame_time >= self.frame_delay:
                    # 清除屏幕
                    self.screen.fill(self.background_color)
                    
                    # 绘制当前帧
                    if frame_index < len(frames):
                        self.screen.blit(frames[frame_index], (0, 0))
                        frame_index += 1
                    
                    # 更新显示
                    pygame.display.flip()
                    last_frame_time = current_time
                
                # 控制帧率
                clock.tick(60)
            
            # 动画播放完成后稍等一下
            if frame_index >= len(frames):
                pygame.time.wait(500)  # 等待500ms
                
            print(f"{animation_type}动画播放完成")
            return True
            
        except Exception as e:
            print(f"播放动画时发生异常: {e}")
            return False
        
        finally:
            # 恢复原始窗口标题
            pygame.display.set_caption(self.original_title)
    
    def play_victory_animation(self) -> bool:
        """播放胜利动画"""
        return self.play_animation('victory')
    
    def play_defeat_animation(self) -> bool:
        """播放失败动画"""
        return self.play_animation('defeat')

def create_animation_player(screen: pygame.Surface) -> AnimationPlayer:
    """
    创建动画播放器实例
    
    :param screen: pygame显示表面
    :return: 动画播放器实例
    """
    return AnimationPlayer(screen)
