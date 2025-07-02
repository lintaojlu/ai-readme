import os
from dotenv import load_dotenv
from typing import Dict, Union

# Load environment variables file
load_dotenv('source.env')


def get_llm_config() -> Dict[str, Union[str, int, float]]:
    """
    Get LLM configuration
    
    Returns:
        LLM configuration dictionary
    """
    return {
        "base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        "api_key": os.getenv("LLM_API_KEY"),
        "model_name": os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1000")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7"))
    }


def get_t2i_config() -> Dict[str, Union[str, int, float]]:
    """
    Get text-to-image configuration
    
    Returns:
        Text-to-image configuration dictionary
    """
    return {
        "base_url": os.getenv("T2I_BASE_URL", "https://api.openai.com/v1"),
        "api_key": os.getenv("T2I_API_KEY"),
        "model_name": os.getenv("T2I_MODEL_NAME", "dall-e-3"),
        "image_size": os.getenv("IMAGE_SIZE", "1024x1024"),
        "quality": os.getenv("QUALITY", "standard")
    }


def validate_config():
    """
    Validate if configuration is complete
    """
    llm_config = get_llm_config()
    t2i_config = get_t2i_config()
    
    if not llm_config["api_key"]:
        raise ValueError("LLM_API_KEY environment variable not set")
    
    if not t2i_config["api_key"]:
        raise ValueError("T2I_API_KEY environment variable not set")
    
    print("Configuration validation passed")
    return True


# Keep original default configurations for use by other modules
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
    "__init__.py",      # 根目录下的 __init__.py
    "*/__init__.py",    # 一级子目录下的 __init__.py
    "*/*/__init__.py",  # 二级子目录下的 __init__.py
    ".idea"
]

# Patterns for script files to be described by the LLM
SCRIPT_PATTERNS = ["*.py", "*.sh"]
DOCUMENT_PATTERNS = ["*.md", "*.txt"]


def get_readme_template_path():
    """Gets the path to the BLANK_README.md template."""
    from importlib import resources
    try:
        with resources.path('readmecraft', 'BLANK_README.md') as p:
            return str(p)
    except FileNotFoundError:
        raise FileNotFoundError("BLANK_README.md not found in package.")


if __name__ == "__main__":
    # Test configuration loading
    print("=== LLM Configuration ===")
    llm_config = get_llm_config()
    for key, value in llm_config.items():
        print(f"{key}: {value}")
    
    print("\n=== Text-to-Image Configuration ===")
    t2i_config = get_t2i_config()
    for key, value in t2i_config.items():
        print(f"{key}: {value}")
    
    print("\n=== Configuration Validation ===")
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration validation failed: {e}")