import pygame
import sys
import os

# 修正导入路径
sys.path.append(os.path.dirname(__file__))
from ui.menu_ui import GameUI, StartMenu, ResultMenu

def test_start_menu():
    """测试开始菜单"""
    print("=== 测试开始菜单 ===")
    start_menu = StartMenu()
    choice = start_menu.run()
    print(f"用户选择: {choice}")
    return choice

def test_result_menu():
    """测试结算菜单"""
    print("=== 测试结算菜单 ===")
    result_menu = ResultMenu()
    
    # 测试显示成功结果
    print("显示成功结果...")
    result_menu.show_result(result=1)
    
    # 测试显示失败结果
    print("显示失败结果...")
    result_menu.show_result(result=0)

def test_game_ui():
    """测试GameUI主接口类"""
    print("=== 测试GameUI主接口类 ===")
    game_ui = GameUI()
    
    # 测试开始菜单
    choice = game_ui.show_start_menu()
    print(f"GameUI开始菜单选择: {choice}")
    
    if choice == "start":
        # 如果选择开始游戏，显示一个结算界面作为演示
        print("模拟游戏结束，显示结算界面...")
        game_ui.show_result_menu(result=1)
    elif choice == "quit":
        print("用户选择退出")
        return "quit"
    
    return choice

def create_test_result_file():
    """创建测试用的结果文件"""
    with open("result.txt", "w") as f:
        f.write("1")  # 写入成功结果
    print("创建测试结果文件 result.txt")

def test_file_reading():
    """测试从文件读取结果"""
    print("=== 测试文件读取功能 ===")
    create_test_result_file()
    
    result_menu = ResultMenu()
    try:
        result = result_menu.read_result("result.txt")
        print(f"从文件读取的结果: {result}")
        result_menu.show_result(filename="result.txt")
    except FileNotFoundError as e:
        print(f"文件读取错误: {e}")
    
    # 清理测试文件
    if os.path.exists("result.txt"):
        os.remove("result.txt")
        print("清理测试文件")

def main():
    """主测试函数"""
    print("五子棋游戏菜单UI测试程序")
    print("=" * 40)
    
    try:
        # 测试1: 测试开始菜单
        choice = test_start_menu()
        
        if choice == "quit":
            print("测试结束")
            return
        
        # 测试2: 测试结算菜单
        test_result_menu()
        
        # 测试3: 测试文件读取功能
        test_file_reading()
        
        # 测试4: 测试完整的GameUI流程
        print("\n" + "=" * 40)
        print("开始完整流程测试...")
        test_game_ui()
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        pygame.quit()
        print("测试完成，程序退出")

if __name__ == "__main__":
    main()
