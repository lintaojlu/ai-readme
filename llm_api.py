# -*- coding: utf-8 -*-
# Author: Lintao
import json
import os
import random
import time
from pathlib import Path
from openai import OpenAI

ROOT_PATH = Path(os.path.abspath(__file__)).parents[0]  # 项目根目录


def get_model_answer(model_name, inputs_list, config_dir=None, stream=False):
    if not config_dir:
        config_dir = ROOT_PATH / 'config'
    if not os.path.exists(os.path.join(config_dir, 'llm_config.json')):
        return "Lack of configuration file. --llm_config.json--"

    answer = 'no answer'
    if 'gpt' in model_name:
        model = OPENAI_API(model_name, user_dir=config_dir)
        answer = model.get_response(inputs_list, stream=stream)
    else:
        model = OPENAI_API(model_name, user_dir=config_dir)  # 代理站中一般可以访问多种OPENAI接口形式的自定义模型，这里作为保底。
        answer = model.get_response(inputs_list, stream=stream)
    return answer


class OPENAI_API:
    def __init__(self, model_name, user_dir):
        self.client = None
        self.USER_DIR = Path(user_dir)
        self.CONFIG_PATH = self.USER_DIR
        # 读取LLM_CONFIG
        OPENAI_CONFIG_PATH = self.CONFIG_PATH / "llm_config.json"
        openai_config_data = json.load(open(OPENAI_CONFIG_PATH, "r"))
        self.keys_bases = openai_config_data["OPENAI_CONFIG"]["OPENAI_KEYS_BASES"]
        self.current_key_index = 0  # 初始索引
        self.api_key, self.api_base = self.keys_bases[self.current_key_index]["OPENAI_KEY"], \
            self.keys_bases[self.current_key_index]["OPENAI_BASE"]

        self.model_name = model_name
        self.max_tokens = openai_config_data["OPENAI_CONFIG"]["OPENAI_MAX_TOKENS"]
        self.temperature = openai_config_data["OPENAI_CONFIG"]["OPENAI_TEMPERATURE"]
        self.stop = None
        self.load_model()

    def load_model(self):
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

    def switch_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.keys_bases)
        new_key_base = self.keys_bases[self.current_key_index]
        self.api_key, self.api_base = new_key_base["OPENAI_KEY"], new_key_base["OPENAI_BASE"]
        self.load_model()
        print(f"Switched to new API key and base: {self.api_key}, {self.api_base}")

    def get_response(self, inputs_list, stream=False, max_retries=3):
        attempt = 0
        while attempt < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=inputs_list,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stop=self.stop
                )
                return response.choices[0].message.content
            except Exception as e:
                attempt += 1
                print(f"Attempt {attempt} failed with error: {e}")
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Waiting {wait_time:.2f} seconds before retrying...")
                    time.sleep(wait_time)
                    self.switch_api_key()  # Optionally switch API key before retrying
                else:
                    return "An error occurred, and the request could not be completed after retries."
