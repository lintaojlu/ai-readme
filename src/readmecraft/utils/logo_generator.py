import os
from rich.console import Console
from readmecraft.utils.model_client import ModelClient

def generate_logo(project_dir, descriptions, model_client, console):
    """
    Generate project logo image based on project description
    
    Args:
        project_dir: Project directory path
        descriptions: Project description information
        model_client: Model client instance
        console: Console output object
        
    Returns:
        str: Generated logo image path, returns None if failed
    """
    console.print("Generating project logo...")
    try:
        # Create images directory
        images_dir = os.path.join(project_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        png_path = os.path.join(images_dir, "logo.png")

        # Step 1: Generate logo description prompt based on project description
        description_prompt = f"""Based on the following project information, generate a professional logo design description:

**Project Information**:
{descriptions}

Please generate a concise, professional logo design description with the following requirements:
1. Description should reflect the core functionality and features of the project
2. Style should be modern, minimalist, and professional
3. Suitable for use as a project logo
4. Include color suggestions and design elements
5. Describe in English, within 50 words

Return only the logo design description, no other explanations.
"""
        
        # Get logo description
        logo_description = model_client.get_answer(description_prompt)
        console.print(f"[cyan]Logo Description: {logo_description}[/cyan]")
        
        # Step 2: Generate image using logo description
        image_prompt = f"A professional, modern, minimalist logo: {logo_description}, don't include any text in the image"
        console.print(f"[cyan]Generating image...[/cyan]")
        
        # Call text-to-image API to generate logo
        image_result = model_client.get_image(image_prompt)
        
        if "error" in image_result:
            console.print(f"[red]Image generation failed: {image_result['error']}[/red]")
            return None
        
        if not image_result["content"]:
            console.print("[red]Image content is empty, generation failed[/red]")
            return None
        
        # Save image file
        with open(png_path, 'wb') as f:
            f.write(image_result["content"])
        
        console.print(f"[green]✔ Logo image saved to {png_path}[/green]")
        console.print(f"[green]✔ Image URL: {image_result['url']}[/green]")
        
        return png_path
            
    except Exception as e:
        console.print(f"[red]Logo generation failed: {e}[/red]")
        return None