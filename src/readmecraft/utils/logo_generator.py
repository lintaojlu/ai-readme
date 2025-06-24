import os
import re
import requests
import drawsvg as draw
from rich.console import Console
from readmecraft.utils.llm import LLM

def generate_logo(project_dir, repo_name, descriptions, llm, console):
    console.print("Generating project logo...")
    try:
        images_dir = os.path.join(project_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        logo_path = os.path.join(images_dir, "logo.png")

        if os.path.exists(logo_path):
            console.print("[green]✔ Logo already exists.[/green]")
            return logo_path

        prompt = f"Based on the project descriptions below, create a simple logo in drawio XML format. The logo should be clean and professional. Only return the XML code for the drawio diagram.\n\n{descriptions}"
        messages = [{"role": "user", "content": prompt}]
        drawio_code = llm.get_answer(messages)

        # Clean up the response to get only the XML
        drawio_code_match = re.search(r'<mxGraphModel.*</mxGraphModel>', drawio_code, re.DOTALL)
        if not drawio_code_match:
            console.print("[red]Failed to get valid drawio XML from LLM.[/red]")
            raise ValueError("No drawio XML found in LLM response")
        drawio_code = drawio_code_match.group(0)

        try:
            # Convert drawio XML to PNG using diagrams.net service
            export_url = "https://convert.diagrams.net/node/export"
            payload = {
                'xml': drawio_code,
                'format': 'png',
            }
            
            response = requests.post(export_url, data=payload)
            response.raise_for_status()

            with open(logo_path, 'wb') as f:
                f.write(response.content)

            console.print(f"[green]✔ Logo generated from drawio and saved at {logo_path}[/green]")
            return logo_path
        except Exception as e:
            console.print(f"[red]Failed to convert drawio to png: {e}[/red]")
            raise e # Reraise to be caught by the outer loop for fallback
            
    except Exception as e:
        console.print(f"[red]Failed to generate logo: {e}[/red]")
        # If everything fails, try to generate a placeholder
        try:
            images_dir = os.path.join(project_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            logo_path = os.path.join(images_dir, "logo.png")
            console.print("Generating placeholder logo as a fallback...")
            d = draw.Drawing(200, 80, origin='center')
            d.append(draw.Rectangle(-100, -40, 200, 80, fill='lightblue'))
            d.append(draw.Text(repo_name, 20, 0, 0, fill='black', text_anchor='middle', dominant_baseline='middle'))
            d.save_png(logo_path)
            console.print(f"[green]✔ Placeholder logo generated at {logo_path}[/green]")
            return logo_path
        except Exception as final_e:
            console.print(f"[red]Failed to generate placeholder logo: {final_e}[/red]")
            return None