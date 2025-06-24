import os
import json
from pathlib import Path
from rich import print

# Default ignore patterns for project structure analysis
DEFAULT_IGNORE_PATTERNS = [
    ".git",
    ".vscode",
    "__pycache__",
    "*.pyc",
    ".DS_Store",
    "build",
    "dist",
    "*.egg-info",
    ".venv",
    "venv",
]

# Patterns for script files to be described by the LLM
SCRIPT_PATTERNS = ["*.py", "*.sh"]

def get_llm_config():
    """
    获取 LLM 配置信息。
    优先级：环境变量 > 配置文件。
    """
    print("[bold cyan]Searching for API configurations...[/bold cyan]")

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("MODEL_NAME")

    config = {}

    if api_key:
        print("[green]✔ Found [bold]OPENAI_API_KEY[/bold] in environment variables.[/green]")
        config["api_key"] = api_key
    else:
        print("[yellow]⚠ [bold]OPENAI_API_KEY[/bold] not found in environment variables.[/yellow]")

    if base_url:
        print("[green]✔ Found [bold]OPENAI_BASE_URL[/bold] in environment variables.[/green]")
        config["base_url"] = base_url
    else:
        print("[yellow]ℹ [bold]OPENAI_BASE_URL[/bold] not found, using default.[/yellow]")

    if model_name:
        print("[green]✔ Found [bold]MODEL_NAME[/bold] in environment variables.[/green]")
        config["model"] = model_name
    else:
        print("[yellow]ℹ [bold]MODEL_NAME[/bold] not found, using default.[/yellow]")

    if config.get("api_key"):
        return config

    config_path = Path.home() / ".config" / "readmecraft" / "user_config.json"
    print(f"[cyan]Searching for configuration file at: [bold]{config_path}[/bold][/cyan]")

    if os.path.exists(config_path):
        print("[green]✔ Found configuration file.[/green]")
        with open(config_path, "r") as f:
            return json.load(f)
    else:
        print(f"[yellow]⚠ Configuration file not found at: [bold]{config_path}[/bold][/yellow]")
        return {}

def get_readme_template_path():
    """Gets the path to the BLANK_README.md template."""
    # Path when installed as a package
    package_path = Path(__file__).parent.parent.parent / 'BLANK_README.md'
    if package_path.exists():
        return str(package_path)
    # Fallback for local development
    local_path = Path.cwd() / 'BLANK_README.md'
    if local_path.exists():
        return str(local_path)
    raise FileNotFoundError("BLANK_README.md not found in package or current directory.")

    return None

def save_config(config):
    """
    将配置保存到用户配置文件。
    """
    config_dir = Path.home() / ".config" / "readmecraft"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "user_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {config_path}")