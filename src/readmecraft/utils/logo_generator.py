import os
import re
from rich.console import Console
from readmecraft.utils.llm import LLM
from readmecraft.utils.image_converter import convert_svg_to_png

def generate_logo(project_dir, descriptions, llm, console):
    console.print("Generating project logo...")
    try:
        # 创建 images 目录
        images_dir = os.path.join(project_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        svg_path = os.path.join(images_dir, "logo.svg")
        png_path = os.path.join(images_dir, "logo.png")

        prompt = f"""Design a modern, minimalist SVG logo with these specifications:

**Design Guidelines**:
1. Create a clean, professional, and visually appealing logo
2. Use simple geometric shapes and minimal colors
3. Ensure the design reflects the project's essence
4. Make it memorable and distinctive
5. Balance negative space effectively

**Technical Requirements**:
1. Pure SVG format for README.md embedding
2. Width: 200px, Height: 60-100px (adaptive)
3. Complete, standalone SVG code
4. URI-encode special characters
5. Code must start with <svg> and end with </svg>
6. Optimize for both light and dark themes

**Project Context**:
{descriptions}

Please provide only the SVG code, no explanations needed.
"""
        messages = [{"role": "user", "content": prompt}]
        svg_code = llm.get_answer(messages)

        # Clean up the response to get only the SVG
        svg_code_match = re.search(r'<svg.*</svg>', svg_code, re.DOTALL)
        if not svg_code_match:
            console.print("[red]Failed to get valid SVG code from LLM.[/red]")
            return None
        
        svg_code = svg_code_match.group(0)
        
        # 保存 SVG 文件
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_code)
        console.print(f"[green]✔ SVG logo saved to {svg_path}[/green]")

        # 转换为 PNG
        convert_svg_to_png(svg_code, png_path)
        console.print(f"[green]✔ PNG logo converted and saved to {png_path}[/green]")

        return png_path
            
    except Exception as e:
        console.print(f"[red]Failed to generate logo: {e}[/red]")
        return None