import argparse
from rich.console import Console
from aireadme.core import aireadme

def main():
    """
    aireadme command line entry point
    Use interactive interface to get project path and output directory
    """
    parser = argparse.ArgumentParser(
        description="aireadme - AI-driven README documentation generator",
        epilog="Use interactive interface to configure project path and output directory"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="aireadme 0.1.8"
    )
    
    # Parse command line arguments (now only --help and --version)
    args = parser.parse_args()

    try:
        # Create aireadme instance using interactive mode
        readme_generator = aireadme()
        readme_generator.generate()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except FileNotFoundError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        console = Console()
        console.print(f"[red]An error occurred: {e}[/red]")