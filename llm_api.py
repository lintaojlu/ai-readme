# -*- coding: utf-8 -*-
# Author: Lintao
import json
import os
import random
import time
from pathlib import Path
from google import genai
from google.genai import types
from openai import OpenAI
import requests
from typing import Dict, List, Union, Optional, Any
import types


class ModelAPI:
    """统一的模型API接口，支持多种LLM平台"""

    def __init__(self, platform: str, model_name: str, config_dir: Union[str, Path]):
        """初始化ModelAPI

        Args:
            platform: 平台名称，如'openai', 'gemini', 'infingence', 'volcengine'
            model_name: 模型名称
            config_dir: 配置文件目录
        """
        self.platform = platform.lower()
        self.model_name = model_name
        self.config_dir = Path(config_dir)
        self.config_data = self._load_config()
        self.max_retries = self._get_max_retries()
        self.model = self._initialize_model()

    def _load_config(self) -> Dict:
        """加载配置文件

        Returns:
            配置数据字典
        """
        config_path = self.config_dir / "llm_config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                return config_data
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件格式错误: {config_path}")

    def _get_max_retries(self) -> int:
        """获取最大重试次数

        Returns:
            最大重试次数
        """
        # 根据平台获取对应的最大重试次数，默认为3
        platform_config_key = f"{self.platform.upper()}_CONFIG"
        if platform_config_key in self.config_data:
            return self.config_data[platform_config_key].get("MAX_RETRIES", 3)
        return 3

    def _initialize_model(self):
        """根据平台初始化对应的API客户端"""
        platform_map = {
            'openai': OPENAI_API,
            'infingence': INFINGENCE_API,
            'gemini': GEMINI_API,
            'deepbricks': Deepbricks_API,
            'volcengine': VOLCENGINE_API
        }

        if self.platform in platform_map:
            platform_config_key = f"{self.platform.upper()}_CONFIG"
            if platform_config_key not in self.config_data:
                raise ValueError(f"配置文件中缺少{platform_config_key}部分")
            platform_config_data = self.config_data[platform_config_key]
            print(f"正在初始化 {self.platform} 平台的 {self.model_name} 模型...")  # 添加日志
            print(f"platform_config_data: {platform_config_data}")  # 添加日志
            model_instance = platform_map[self.platform](self.model_name, platform_config_data)
            print(f"{self.platform} 平台的 {self.model_name} 模型初始化成功")  # 添加成功日志
            return model_instance
        else:
            supported_platforms = list(platform_map.keys())
            print(f"不支持的平台: {self.platform}. 支持的平台有: {supported_platforms}")  # 添加错误日志
            raise ValueError(f"Unsupported platform: {self.platform}. Supported platforms: {supported_platforms}")

    def get_answer(self, inputs_list: List[Dict[str, str]], stream: bool = False) -> Union[str, Any]:
        """获取模型回答

        Args:
            inputs_list: 输入消息列表，格式为[{"role": "...", "content": "..."}]
            stream: 是否使用流式生成

        Returns:
            如果stream=False，返回字符串回答
            如果stream=True，返回流式生成对象
        """
        attempt = 0
        last_exception = None

        while attempt < self.max_retries:
            try:
                return self.model.get_response(inputs_list, stream=stream)
            except Exception as e:
                attempt += 1
                last_exception = e
                print(f"Attempt {attempt} failed with error: {e}")
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # 指数退避策略
                    print(f"Waiting {wait_time:.2f} seconds before retrying...")
                    time.sleep(wait_time)

        # 所有重试都失败
        error_msg = f"An error occurred, and the request could not be completed after {self.max_retries} retries. Error: {last_exception}"
        print(error_msg)
        return error_msg


class OPENAI_API:
    """OpenAI API客户端，支持流式和非流式生成"""

    def __init__(self, model_name: str, platform_config_data: Dict):
        # 验证配置数据
        self.keys_bases = platform_config_data.get("OPENAI_KEYS_BASES", [])
        if not self.keys_bases:
            raise ValueError("OpenAI API密钥未配置")

        self.current_key_index = 0  # 初始索引
        self.api_key, self.api_base = self.keys_bases[self.current_key_index]["OPENAI_KEY"], \
            self.keys_bases[self.current_key_index]["OPENAI_BASE"]

        self.model_name = model_name
        self.max_tokens = platform_config_data.get("OPENAI_MAX_TOKENS", 4096)
        self.temperature = platform_config_data.get("OPENAI_TEMPERATURE", 0.7)
        self.stop = None
        self.client = None
        self.load_model()

    def load_model(self):
        """初始化OpenAI客户端"""
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

    def switch_api_key(self):
        """切换到下一个API密钥"""
        self.current_key_index = (self.current_key_index + 1) % len(self.keys_bases)
        new_key_base = self.keys_bases[self.current_key_index]
        self.api_key, self.api_base = new_key_base["OPENAI_KEY"], new_key_base["OPENAI_BASE"]
        self.load_model()
        print(f"Switched to new API key and base: {self.api_key}, {self.api_base}")

    def get_response(self, inputs_list: List[Dict[str, str]], stream: bool = False) -> Union[str, Any]:
        """获取模型回答

        Args:
            inputs_list: 输入消息列表
            stream: 是否使用流式生成

        Returns:
            如果stream=False，返回字符串回答
            如果stream=True，返回流式生成对象
        """
        try:
            if stream:
                stream_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=inputs_list,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True,
                )

                def generate():
                    for chunk in stream_response:
                        if chunk.choices and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta,
                                                                                            'content') and \
                                chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                return generate()
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=inputs_list,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stop=self.stop,
                    stream=False
                )
                return response.choices[0].message.content
        except Exception as e:
            # 如果发生错误，尝试切换API密钥后重新抛出异常，让ModelAPI处理重试
            self.switch_api_key()
            raise e


class GEMINI_API:
    """Gemini API客户端，支持流式和非流式生成"""

    def __init__(self, model_name: str, platform_config_data: Dict):
        # 验证配置数据
        self.api_key = platform_config_data.get("API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API密钥未配置")

        # 验证模型配置
        models = platform_config_data.get("MODELS", {})
        if model_name not in models and not platform_config_data.get("ALLOW_ANY_MODEL", False):
            available_models = list(models.keys())
            raise ValueError(f"模型名称'{model_name}'在配置中未找到。可用模型: {available_models}")

        # 初始化客户端
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = models.get(model_name, model_name)  # 使用配置中的模型名称映射

        # 获取生成参数配置
        self.temperature = platform_config_data.get("TEMPERATURE", 0.7)
        self.max_tokens = platform_config_data.get("MAX_TOKENS", 4096)

        # 配置生成参数
        self.config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }

    def _get_stream_response(self, inputs_list: List[Dict[str, str]]) -> Any:
        """获取流式响应

        Args:
            inputs_list: 输入消息列表

        Returns:
            流式生成对象
        """
        # 将消息列表转换为Gemini格式的提示
        prompt = self._convert_messages_to_prompt(inputs_list)

        # 获取流式响应
        response = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=[prompt],
            config=self.config
        )

        def generate():
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text

        return generate()

    def _get_normal_response(self, inputs_list: List[Dict[str, str]]) -> str:
        """获取普通响应

        Args:
            inputs_list: 输入消息列表

        Returns:
            生成的文本响应
        """
        # 将消息列表转换为Gemini格式的提示
        prompt = self._convert_messages_to_prompt(inputs_list)

        # 获取普通响应
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt],
            config=self.config
        )

        return response.text

    def _convert_messages_to_prompt(self, inputs_list: List[Dict[str, str]]) -> str:
        """将消息列表转换为Gemini格式的提示

        Args:
            inputs_list: 输入消息列表

        Returns:
            Gemini格式的提示文本
        """
        prompt = ""
        for msg in inputs_list:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt += f"system: {content}\n\n"
            elif role == "user":
                prompt += f"user: {content}\n"
            elif role == "assistant":
                prompt += f"assistant: {content}\n"

        return prompt.strip()

    def get_response(self, inputs_list: List[Dict[str, str]], stream: bool = False) -> Union[str, Any]:
        """获取模型回答

        Args:
            inputs_list: 输入消息列表
            stream: 是否使用流式生成

        Returns:
            如果stream=False，返回字符串回答
            如果stream=True，返回流式生成对象
        """
        try:
            if stream:
                return self._get_stream_response(inputs_list)
            else:
                return self._get_normal_response(inputs_list)
        except Exception as e:
            print(f"Gemini API调用失败: {str(e)}")
            raise e


class INFINGENCE_API:
    """Infingence API客户端，支持流式和非流式生成"""

    def __init__(self, model_name: str, platform_config_data: Dict):
        # 验证配置数据
        self.api_key = platform_config_data.get("API_KEY")
        if not self.api_key:
            raise ValueError("Infingence API密钥未配置")

        models = platform_config_data.get("MODELS", {})
        self.api_url = models.get(model_name)

        if not self.api_url:
            raise ValueError(f"模型名称'{model_name}'在配置中未找到。可用模型: {list(models.keys())}")

        self.model_name = model_name

    def get_response(self, inputs_list: List[Dict[str, str]], stream: bool = False) -> Union[str, Any]:
        """获取模型回答

        Args:
            inputs_list: 输入消息列表
            stream: 是否使用流式生成

        Returns:
            如果stream=False，返回字符串回答
            如果stream=True，返回流式生成对象
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        payload = json.dumps({
            "model": self.model_name,
            "messages": inputs_list,
            "stream": stream
        })

        if stream:
            with requests.post(self.api_url, headers=headers, data=payload, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    raise Exception(error_msg)

                def generate():
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8').lstrip('data: '))
                                if 'choices' in data and len(data['choices']) > 0:
                                    if 'delta' in data['choices'][0] and 'content' in data['choices'][0]['delta']:
                                        content = data['choices'][0]['delta']['content']
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                continue

                return generate()
        else:
            response = requests.post(self.api_url, headers=headers, data=payload, timeout=60)
            if response.status_code != 200:
                error_msg = f"Error: {response.status_code} - {response.text}"
                raise Exception(error_msg)

            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            return answer


class Deepbricks_API:
    """Deepbricks API客户端，用于图像生成"""

    def __init__(self, model_name: str, platform_config_data: Dict):
        # 验证配置数据
        self.model_name = model_name
        self.api_key = platform_config_data.get("API_KEY")
        if not self.api_key:
            raise ValueError("Deepbricks API密钥未配置")

        self.base_url = platform_config_data.get("BASE_URL")
        if not self.base_url:
            raise ValueError("Deepbricks BASE_URL未配置")

        # 初始化客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 设置重试参数
        self.max_retries = platform_config_data.get("MAX_RETRIES", 3)

    def get_picture(self, save_path: str, prompt: str, size: str = '1792x1024', quality: str = 'hd',
                    max_retries: int = None) -> str:
        """
        生成图片并保存到指定路径

        Args:
            save_path: 保存图片的路径
            prompt: 图片生成提示词
            size: 图片尺寸，如'1792x1024'
            quality: 图片质量，如'hd'
            max_retries: 最大重试次数，如果为None则使用配置中的值

        Returns:
            成功返回'Success'，失败返回错误信息
        """
        # 使用配置中的重试次数，如果未指定
        if max_retries is None:
            max_retries = self.max_retries

        attempt = 0
        last_exception = None

        while attempt < max_retries:
            try:
                resp = self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size=size,
                    quality=quality)

                # 下载并保存图片
                image_resp = requests.get(resp.data[0].url, timeout=30)
                image_resp.raise_for_status()  # 确保请求成功

                # 确保目标目录存在
                save_dir = os.path.dirname(save_path)
                if save_dir and not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)

                with open(save_path, "wb") as fw:
                    fw.write(image_resp.content)

                return 'Success'
            except Exception as e:
                attempt += 1
                last_exception = e
                print(f"Attempt {attempt} failed with error: {e}")
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Waiting {wait_time:.2f} seconds before retrying...")
                    time.sleep(wait_time)

        # 所有重试都失败
        error_msg = f"An error occurred, and the request could not be completed after {max_retries} retries. Error: {last_exception}"
        print(error_msg)
        return error_msg

    def get_response(self, inputs_list: List[Dict[str, str]], stream: bool = False) -> str:
        """
        为了与其他API类保持接口一致而添加的方法
        Deepbricks主要用于图像生成，不支持文本对话

        Args:
            inputs_list: 输入消息列表
            stream: 是否使用流式生成

        Returns:
            提示用户使用get_picture方法的消息
        """
        return "Deepbricks API is for image generation. Please use get_picture method instead."


class VOLCENGINE_API:
    """火山引擎API客户端，支持流式和非流式生成"""

    def __init__(self, model_name: str, platform_config_data: Dict):
        # 验证配置数据
        self.api_key = platform_config_data.get("API_KEY")
        if not self.api_key:
            raise ValueError("火山引擎API密钥未配置")

        self.base_url = platform_config_data.get("BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

        # 获取模型配置
        self.model_name = model_name
        models = platform_config_data.get("MODELS", {})
        if self.model_name not in models and not platform_config_data.get("ALLOW_ANY_MODEL", False):
            available_models = list(models.keys())
            raise ValueError(f"模型名称'{model_name}'在配置中未找到。可用模型: {available_models}")

        # 获取模型对应的endpoint
        self.model_endpoint = models.get(self.model_name)

        # 获取其他配置参数
        self.max_tokens = platform_config_data.get("MAX_TOKENS", 4096)
        self.temperature = platform_config_data.get("TEMPERATURE", 0.7)
        self.max_retries = platform_config_data.get("MAX_RETRIES", 3)

        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def get_response(self, inputs_list: List[Dict[str, str]], stream: bool = False) -> Union[str, Any]:
        """
        获取模型回答

        Args:
            inputs_list: 输入消息列表
            stream: 是否使用流式生成

        Returns:
            如果stream=False，返回字符串回答
            如果stream=True，返回流式生成对象
        """
        attempt = 0
        last_exception = None

        while attempt < self.max_retries:
            try:
                if stream:
                    stream_response = self.client.chat.completions.create(
                        model=self.model_endpoint,
                        messages=inputs_list,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        stream=True,
                    )

                    def generate():
                        for chunk in stream_response:
                            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and \
                                    chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content

                    return generate()
                else:
                    response = self.client.chat.completions.create(
                        model=self.model_endpoint,
                        messages=inputs_list,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        stream=False
                    )
                    return response.choices[0].message.content

            except Exception as e:
                attempt += 1
                last_exception = e
                print(f"Attempt {attempt} failed with error: {e}")

                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # 指数退避策略
                    print(f"Waiting {wait_time:.2f} seconds before retrying...")
                    time.sleep(wait_time)

        # 所有重试都失败
        error_msg = f"An error occurred, and the request could not be completed after {self.max_retries} retries. Error: {last_exception}"
        print(error_msg)
        return error_msg


if __name__ == '__main__':
    # 配置目录路径
    LLM_CONFIG_DIR = Path(os.path.abspath(__file__)).parent / "config"

    # 简单的测试消息
    simple_test_messages = [
        {"role": "system", "content": "你是一个有用的AI助手。"},
        {"role": "user", "content": "你好，请简单介绍一下自己。100字以内"}
    ]


    # 测试不同平台的API
    def test_api(platform, model_name, messages=None, stream=False):
        if messages is None:
            messages = simple_test_messages

        print(f"\n{'=' * 50}")
        print(f"测试 {platform.upper()} API - 模型: {model_name}")
        print(f"{'=' * 50}")

        try:
            model_api = ModelAPI(platform=platform, model_name=model_name, config_dir=LLM_CONFIG_DIR)

            if stream:
                start_time = time.time()
                print(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")}] [流式生成回答]')
                is_first_chunk = True
                for chunk in model_api.get_answer(messages, stream=True):
                    if is_first_chunk:
                        first_chunk_time = time.time()
                        time_diff = int((first_chunk_time - start_time) * 1000)  # 转换为毫秒
                        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] [耗时: {time_diff}ms] {chunk}', end="",
                              flush=True)
                        is_first_chunk = False
                    else:
                        print(chunk, end="", flush=True)
                print()  # 最后换行
            else:
                start_time = time.time()
                print(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")}] [非流式生成回答]')
                response = model_api.get_answer(messages, stream=False)
                end_time = time.time()
                time_diff = int((end_time - start_time) * 1000)  # 转换为毫秒
                print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] [耗时: {time_diff}ms] Response: {response}')

        except Exception as e:
            print(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")}] [错误] {platform.upper()} API测试失败: {e}')


    # 根据命令行参数选择要测试的平台
    import sys

    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        if platform == 'openai':
            test_api('openai', 'gpt-3.5-turbo', stream=True)
            test_api('openai', 'gpt-3.5-turbo', stream=False)
        elif platform == 'gemini':
            test_api('gemini', 'gemini-2.0-flash', stream=True)
            test_api('gemini', 'gemini-2.0-flash', stream=False)
        elif platform == 'infingence':
            test_api('infingence', 'qwen2.5-7b-instruct', stream=True)
            test_api('infingence', 'qwen2.5-7b-instruct', stream=False)
        elif platform == 'volcengine':
            test_api('volcengine', 'deepseek-v3', stream=True)
            # test_api('volcengine', 'deepseek-v3', stream=False)
        elif platform == 'all':
            # 测试所有平台
            test_api('openai', 'gpt-3.5-turbo', stream=True)
            # test_api('gemini', 'gemini-pro')
            # test_api('infingence', 'qwen2.5-7b-instruct', stream=False)
            test_api('volcengine', 'deepseek-v3', stream=True)
        else:
            print(f"未知平台: {platform}")
            print("可用平台: openai, gemini, infingence, volcengine, all")
    else:
        # 默认测试OpenAI API
        test_api('openai', 'gpt-3.5-turbo', stream=False)

