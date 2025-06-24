import argparse
import os
from readmecraft.core import readmecraft

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
        readme_generator = readmecraft(args.project_dir)
        readme_generator.generate()
    except Exception as e:
        print(f"Error: {e}")