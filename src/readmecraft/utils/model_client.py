import os
import requests
from openai import OpenAI
from typing import Optional, Dict, Union
from readmecraft.config import get_llm_config, get_t2i_config, validate_config


class ModelClient:
    """模型客户端类，用于LLM问答和文生图功能"""
    
    def __init__(self, max_tokens: int = 1000, temperature: float = 0.7, 
                 image_size: str = "1024x1024", quality: str = "hd"):
        """
        初始化模型客户端
        
        Args:
            max_tokens: 最大token数量
            temperature: 温度参数
            image_size: 图片尺寸
            quality: 图片质量
        """
        # 验证配置
        validate_config()
        
        # 获取配置
        self.llm_config = get_llm_config()
        self.t2i_config = get_t2i_config()
        
        # 设置参数
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.image_size = image_size
        self.quality = quality
        
        # 初始化客户端
        self.llm_client = self._initialize_llm_client()
        self.t2i_client = self._initialize_t2i_client()
    
    def _initialize_llm_client(self) -> OpenAI:
        """
        初始化LLM客户端
        
        Returns:
            配置好的LLM OpenAI客户端
        """
        return OpenAI(
            base_url=self.llm_config["base_url"],
            api_key=self.llm_config["api_key"],
        )
    
    def _initialize_t2i_client(self) -> OpenAI:
        """
        初始化文生图客户端
        
        Returns:
            配置好的文生图OpenAI客户端
        """
        return OpenAI(
            base_url=self.t2i_config["base_url"],
            api_key=self.t2i_config["api_key"],
        )
    
    def get_answer(self, question: str, model: Optional[str] = None) -> str:
        """
        使用LLM获取问题的回答
        
        Args:
            question: 用户问题
            model: 指定使用的模型，如果不指定则使用配置中的默认模型
            
        Returns:
            LLM的回答
        """
        try:
            # 使用指定模型或配置中的默认LLM模型
            model_name = model or self.llm_config["model_name"]
            
            response = self.llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": question}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"获取回答时发生错误: {str(e)}"
    
    def get_image(self, prompt: str, model: Optional[str] = None) -> Dict[str, Union[str, bytes, None]]:
        """
        使用文生图模型生成图片
        
        Args:
            prompt: 图片描述prompt
            model: 指定使用的模型，如果不指定则使用配置中的默认模型
            
        Returns:
            包含url和content的字典: {"url": str, "content": bytes}
        """
        try:
            # 使用指定模型或配置中的默认文生图模型
            model_name = model or self.t2i_config["model_name"]
            
            # 生成图片请求参数
            generate_params = {
                "model": model_name,
                "prompt": prompt,
                "n": 1,
                "size": self.image_size
            }
            
            # 如果模型支持quality参数，则添加
            if model_name.startswith("dall-e"):
                generate_params["quality"] = self.quality
            
            response = self.t2i_client.images.generate(**generate_params)
            
            image_url = response.data[0].url
            
            # 下载图片内容，增加重试机制
            image_content = self._download_image_with_retry(image_url, max_retries=3)
            
            print(f"图片URL: {image_url}")
            print(f"图片内容大小: {len(image_content)} 字节")
            
            return {
                "url": image_url,
                "content": image_content
            }
            
        except Exception as e:
            return {
                "url": None,
                "content": None,
                "error": f"生成图片时发生错误: {str(e)}"
            }
    
    def _download_image_with_retry(self, image_url: str, max_retries: int = 3) -> Optional[bytes]:
        """
        带重试机制的图片下载
        
        Args:
            image_url: 图片URL
            max_retries: 最大重试次数
            
        Returns:
            图片内容字节，失败返回None
        """
        import time
        import ssl
        
        for attempt in range(max_retries):
            try:
                print(f"正在下载图片 (尝试 {attempt + 1}/{max_retries})...")
                
                # 设置请求参数，增加SSL容错
                session = requests.Session()
                session.verify = True  # 验证SSL证书
                
                # 增加User-Agent和其他头部
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'image/*,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }
                
                response = session.get(
                    image_url, 
                    timeout=60,  # 增加超时时间
                    headers=headers,
                    stream=True  # 流式下载
                )
                response.raise_for_status()
                
                # 获取图片内容
                image_content = response.content
                print(f"图片下载成功，大小: {len(image_content)} 字节")
                return image_content
                
            except (requests.exceptions.SSLError, ssl.SSLError) as ssl_error:
                print(f"SSL错误 (尝试 {attempt + 1}/{max_retries}): {str(ssl_error)}")
                if attempt == max_retries - 1:
                    print("SSL连接持续失败，可能是服务器证书问题")
                else:
                    time.sleep(2 ** attempt)  # 指数退避
                    
            except requests.exceptions.ConnectionError as conn_error:
                print(f"连接错误 (尝试 {attempt + 1}/{max_retries}): {str(conn_error)}")
                if attempt == max_retries - 1:
                    print("网络连接持续失败")
                else:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.Timeout as timeout_error:
                print(f"超时错误 (尝试 {attempt + 1}/{max_retries}): {str(timeout_error)}")
                if attempt == max_retries - 1:
                    print("请求超时")
                else:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"下载图片失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    print("所有重试都失败了")
                else:
                    time.sleep(1)
        
        return None

    def get_current_settings(self) -> dict:
        """
        获取当前的设置信息
        
        Returns:
            当前设置字典
        """
        return {
            "llm_base_url": self.llm_config["base_url"],
            "llm_model_name": self.llm_config["model_name"],
            "t2i_base_url": self.t2i_config["base_url"],
            "t2i_model_name": self.t2i_config["model_name"],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "image_size": self.image_size,
            "quality": self.quality
        }


def main():
    """主函数，演示模型客户端的使用"""
    try:
        # 创建模型客户端实例
        client = ModelClient()
        
        # 显示当前配置信息
        print("=== 当前配置信息 ===")
        settings = client.get_current_settings()
        for key, value in settings.items():
            print(f"{key}: {value}")
        print()
        
        # 测试LLM问答功能
        print("=== LLM问答测试 ===")
        question = "什么是人工智能？请用50字以内简要回答。"
        answer = client.get_answer(question)
        print(f"问题: {question}")
        print(f"回答: {answer}")
        print()
        
        # 测试文生图功能
        print("=== 文生图测试 ===")
        image_prompt = "一只可爱的小猫在花园里玩耍，卡通风格"
        image_result = client.get_image(image_prompt)
        print(f"图片描述: {image_prompt}")
        
        if "error" in image_result:
            print(f"生成失败: {image_result['error']}")
        else:
            print(f"生成的图片URL: {image_result['url']}")
            if image_result['content']:
                content_size = len(image_result['content'])
                print(f"图片内容大小: {content_size} 字节")
                # 可以选择保存图片到本地
                # with open("generated_image.png", "wb") as f:
                #     f.write(image_result['content'])
                # print("图片已保存为 generated_image.png")
            else:
                print("图片内容下载失败")
        print()
        
        print("=== 程序运行完成 ===")
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")


if __name__ == "__main__":
    main()