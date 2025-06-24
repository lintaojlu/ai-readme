import argparse
import os
from rich.console import Console
from readmecraft.core import ReadmeCraft

def main():
    parser = argparse.ArgumentParser(description="Automatically generate a README.md for your project.")
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=os.getcwd(),
        help="The path to the project directory (default: current directory)."
    )
    args = parser.parse_args()

    try:
        try:
            readme_generator = ReadmeCraft(args.project_dir)
            readme_generator.generate()
        except FileNotFoundError as e:
            console = Console()
            console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        print(f"Error: {e}")