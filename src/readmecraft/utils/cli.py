import argparse
from rich.console import Console
from readmecraft.core import ReadmeCraft

def main():
    """
    ReadmeCraft 命令行入口点
    使用交互式界面获取项目路径和输出目录
    """
    parser = argparse.ArgumentParser(
        description="ReadmeCraft - AI驱动的README文档生成器",
        epilog="使用交互式界面配置项目路径和输出目录"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="ReadmeCraft 0.1.8"
    )
    
    # 解析命令行参数（现在只有 --help 和 --version）
    args = parser.parse_args()

    try:
        # 使用交互式模式创建 ReadmeCraft 实例
        readme_generator = ReadmeCraft()
        readme_generator.generate()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]操作已取消[/yellow]")
    except FileNotFoundError as e:
        console = Console()
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console = Console()
        console.print(f"[red]发生错误: {e}[/red]")