import os
from dotenv import load_dotenv
from typing import Dict, Union

# 加载环境变量文件
load_dotenv('source.env')


def get_llm_config() -> Dict[str, Union[str, int, float]]:
    """
    获取LLM配置
    
    Returns:
        LLM配置字典
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
    获取文生图配置
    
    Returns:
        文生图配置字典
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
    验证配置是否完整
    """
    llm_config = get_llm_config()
    t2i_config = get_t2i_config()
    
    if not llm_config["api_key"]:
        raise ValueError("LLM_API_KEY 环境变量未设置")
    
    if not t2i_config["api_key"]:
        raise ValueError("T2I_API_KEY 环境变量未设置")
    
    print("配置验证通过")
    return True


# 保留原有的默认配置，供其他模块使用
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


def get_readme_template_path():
    """Gets the path to the BLANK_README.md template."""
    from importlib import resources
    try:
        with resources.path('readmecraft', 'BLANK_README.md') as p:
            return str(p)
    except FileNotFoundError:
        raise FileNotFoundError("BLANK_README.md not found in package.")


if __name__ == "__main__":
    # 测试配置加载
    print("=== LLM 配置 ===")
    llm_config = get_llm_config()
    for key, value in llm_config.items():
        print(f"{key}: {value}")
    
    print("\n=== 文生图配置 ===")
    t2i_config = get_t2i_config()
    for key, value in t2i_config.items():
        print(f"{key}: {value}")
    
    print("\n=== 配置验证 ===")
    try:
        validate_config()
    except ValueError as e:
        print(f"配置验证失败: {e}")