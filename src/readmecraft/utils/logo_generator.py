import os
from rich.console import Console
from readmecraft.utils.model_client import ModelClient

def generate_logo(project_dir, descriptions, model_client, console):
    """
    根据项目描述生成项目logo图片
    
    Args:
        project_dir: 项目目录路径
        descriptions: 项目描述信息
        model_client: 模型客户端实例
        console: 控制台输出对象
        
    Returns:
        str: 生成的logo图片路径，失败返回None
    """
    console.print("Generating project logo...")
    try:
        # 创建 images 目录
        images_dir = os.path.join(project_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        png_path = os.path.join(images_dir, "logo.png")

        # 第一步：根据项目描述生成logo描述prompt
        description_prompt = f"""基于以下项目信息，生成一个专业的logo设计描述：

**项目信息**:
{descriptions}

请生成一个简洁、专业的logo设计描述，要求：
1. 描述要体现项目的核心功能和特点
2. 风格要现代、简约、专业
3. 适合作为项目logo使用
4. 包含颜色建议和设计元素
5. 用英文描述，50字以内

只返回logo设计描述，不要其他解释。
"""
        
        # 获取logo描述
        logo_description = model_client.get_answer(description_prompt)
        console.print(f"[cyan]Logo 描述: {logo_description}[/cyan]")
        
        # 第二步：使用logo描述生成图片
        image_prompt = f"A professional, modern, minimalist logo: {logo_description}"
        console.print(f"[cyan]生成图片中...[/cyan]")
        
        # 调用文生图接口生成logo
        image_result = model_client.get_image(image_prompt)
        
        if "error" in image_result:
            console.print(f"[red]图片生成失败: {image_result['error']}[/red]")
            return None
        
        if not image_result["content"]:
            console.print("[red]图片内容为空，生成失败[/red]")
            return None
        
        # 保存图片文件
        with open(png_path, 'wb') as f:
            f.write(image_result["content"])
        
        console.print(f"[green]✔ Logo图片已保存到 {png_path}[/green]")
        console.print(f"[green]✔ 图片URL: {image_result['url']}[/green]")
        
        return png_path
            
    except Exception as e:
        console.print(f"[red]生成logo失败: {e}[/red]")
        return None