import os
import json

def get_config():
    """
    获取配置信息。
    优先级：环境变量 > 配置文件。
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model_name = os.environ.get("MODEL_NAME")

    if api_key:
        config = {"api_key": api_key}
        if base_url:
            config["base_url"] = base_url
        if model_name:
            config["model"] = model_name
        return config

    config_path = os.path.expanduser("~/.config/autoreadme/user_config.json")

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)

    return None

def save_config(config):
    """
    将配置保存到用户配置文件。
    """
    config_dir = os.path.expanduser("~/.config/autoreadme")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "user_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {config_path}")