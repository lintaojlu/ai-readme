import os
import re
from rich.console import Console
from readmecraft.utils.llm import LLM

def generate_logo_svg(descriptions, llm, console):
    console.print("Generating project logo as SVG...")
    try:
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
        console.print("[green]✔ SVG logo generated successfully.[/green]")
        return svg_code
            
    except Exception as e:
        console.print(f"[red]Failed to generate SVG logo: {e}[/red]")
        return None