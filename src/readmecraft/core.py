import os
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from readmecraft.utils.model_client import ModelClient
from readmecraft.utils.file_handler import (
    find_files,
    get_project_structure,
    load_gitignore_patterns,
)
from readmecraft.utils.logo_generator import generate_logo
from .config import DEFAULT_IGNORE_PATTERNS, SCRIPT_PATTERNS, DOCUMENT_PATTERNS, get_readme_template_path


class ReadmeCraft:
    def __init__(self, project_dir=None):
        self.model_client = ModelClient(quality="hd", image_size="1024x1024")  # 确保使用高质量、高分辨率图像生成
        self.console = Console()
        self.project_dir = project_dir  # 初始化时设置项目目录
        self.output_dir = None  # 输出目录将在 _get_basic_info 中设置
        self.config = {
            "github_username": "",
            "repo_name": "",
            "twitter_handle": "",
            "linkedin_username": "",
            "email": "",
            "project_description": "",
            "entry_file": "",
            "key_features": "",
            "additional_info": "",
        }

    def generate(self):
        self._get_basic_info()
        self._get_git_info()
        self._get_user_info()
        self.console.print("[bold green]Generating README...[/bold green]")

        structure = self._generate_project_structure()
        dependencies = self._generate_project_dependencies()
        descriptions = self._generate_script_descriptions()
        logo_path = generate_logo(
            self.output_dir, descriptions, self.model_client, self.console
        )

        readme_content = self._generate_readme_content(
            structure, dependencies, descriptions, logo_path
        )

        # Save README.md to output directory
        readme_path = os.path.join(self.output_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        self.console.print(
            f"[bold green]✔ README.md generated at: {readme_path}[/bold green]"
        )
        if logo_path:
            self.console.print(f"[bold green]✔ Logo generated at: {logo_path}[/bold green]")
        
        # Display all generated files
        self.console.print(f"\n[bold cyan]📁 Generated Files List:[/bold cyan]")
        self.console.print(f"   📄 README.md")
        self.console.print(f"   📋 project_structure.txt")
        self.console.print(f"   📦 requirements.txt") 
        self.console.print(f"   📊 dependencies_analysis.txt")
        self.console.print(f"   📝 script_descriptions.json")
        if logo_path:
            self.console.print(f"   🎨 images/logo.png")
        
        self.console.print(
            f"\n[bold green]✔ All files saved to output directory: {self.output_dir}[/bold green]"
        )

    def _get_basic_info(self):
        """
        Interactive input for basic information: project path and output directory
        """
        self.console.print("[bold cyan]ReadmeCraft - AI README Generator[/bold cyan]")
        self.console.print("Please configure basic information (press Enter to use default values)\n")

        # Get project path
        current_dir = os.getcwd()
        project_input = self.console.input(
            f"[cyan]Project Path[/cyan] (default: {current_dir}): "
        ).strip()

        if project_input:
            # Handle relative and absolute paths
            if os.path.isabs(project_input):
                self.project_dir = project_input
            else:
                self.project_dir = os.path.join(current_dir, project_input)
        else:
            self.project_dir = current_dir

        # Check if project path exists
        if not os.path.exists(self.project_dir):
            self.console.print(f"[red]Error: Project path '{self.project_dir}' does not exist[/red]")
            exit(1)

        self.console.print(f"[green]✔ Project path: {self.project_dir}[/green]")

        # Get output directory
        output_input = self.console.input(
            f"[cyan]Output Directory[/cyan] (default: {current_dir}): "
        ).strip()

        if output_input:
            # Handle relative and absolute paths
            if os.path.isabs(output_input):
                output_base = output_input
            else:
                output_base = os.path.join(current_dir, output_input)
        else:
            output_base = current_dir

        # Create aireadme_output subdirectory under output directory
        self.output_dir = os.path.join(output_base, "aireadme_output")

        # Create output directory
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            self.console.print(f"[green]✔ Output directory: {self.output_dir}[/green]")
        except Exception as e:
            self.console.print(
                f"[red]Error: Cannot create output directory '{self.output_dir}': {e}[/red]"
            )
            exit(1)

        self.console.print()  # Empty line separator

        # Get additional project information
        self.console.print("[bold cyan]Additional Project Information[/bold cyan]")
        self.console.print("Please provide additional information about your project (press Enter to skip):\n")

        # Project description
        self.config["project_description"] = self.console.input(
            "[cyan]Project Description[/cyan] (brief summary of what this project does): "
        ).strip() or ""

        # Entry file
        self.config["entry_file"] = self.console.input(
            "[cyan]Entry File[/cyan] (main file to run the project, e.g., main.py, app.py): "
        ).strip() or ""

        # Features
        self.config["key_features"] = self.console.input(
            "[cyan]Key Features[/cyan] (main features or capabilities, separate with commas): "
        ).strip() or ""

        # Additional information
        self.config["additional_info"] = self.console.input(
            "[cyan]Additional Info[/cyan] (any other important information about the project): "
        ).strip() or ""

        self.console.print("\n[green]✔ Project information collected![/green]")
        self.console.print()  # Empty line separator

    def _get_git_info(self):
        self.console.print("Gathering Git information...")
        try:
            git_config_path = os.path.join(self.project_dir, ".git", "config")
            if os.path.exists(git_config_path):
                with open(git_config_path, "r") as f:
                    config_content = f.read()
                url_match = re.search(
                    r"url =.*github.com[:/](.*?)/(.*?).git", config_content
                )
                if url_match:
                    self.config["github_username"] = url_match.group(1)
                    self.config["repo_name"] = url_match.group(2)
                    self.console.print("[green]✔ Git information gathered.[/green]")
                    self.console.print(f"[green]✔ GitHub Username: {self.config['github_username']}[/green]")
                    self.console.print(f"[green]✔ Repository Name: {self.config['repo_name']}[/green]")
                    return
        except Exception as e:
            self.console.print(f"[yellow]Could not read .git/config: {e}[/yellow]")

        self.console.print(
            "[yellow]Git info not found, please enter manually (or press Enter to use defaults):[/yellow]"
        )
        self.config["github_username"] = self.console.input("[cyan]GitHub Username (default: your-username): [/cyan]") or "your-username"
        self.config["repo_name"] = self.console.input("[cyan]Repository Name (default: your-repo): [/cyan]") or "your-repo"

    def _get_user_info(self):
        self.console.print(
            "Please enter your contact information (or press Enter to use defaults):"
        )
        self.config["twitter_handle"] = self.console.input("[cyan]Twitter Handle (default: @your_handle): [/cyan]") or "@your_handle"
        self.config["linkedin_username"] = self.console.input("[cyan]LinkedIn Username (default: your-username): [/cyan]") or "your-username"
        self.config["email"] = self.console.input("[cyan]Email (default: your.email@example.com): [/cyan]") or "your.email@example.com"

    def _generate_project_structure(self):
        self.console.print("Generating project structure...")
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + gitignore_patterns
        structure = get_project_structure(self.project_dir, ignore_patterns)
        
        # Save project structure to output folder
        if self.output_dir:
            structure_path = os.path.join(self.output_dir, "project_structure.txt")
            with open(structure_path, "w", encoding="utf-8") as f:
                f.write(structure)
            self.console.print(f"[green]✔ Project structure saved to: {structure_path}[/green]")
        
        self.console.print("[green]✔ Project structure generated.[/green]")
        return structure

    def _generate_project_dependencies(self):
        self.console.print("Generating project dependencies...")
        
        # First check if requirements.txt already exists
        existing_requirements_path = os.path.join(self.project_dir, "requirements.txt")
        existing_dependencies = ""
        if os.path.exists(existing_requirements_path):
            with open(existing_requirements_path, "r", encoding="utf-8") as f:
                existing_dependencies = f.read()
            self.console.print("[yellow]Found existing requirements.txt[/yellow]")
        
        # Scan all Python files to extract import statements
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + gitignore_patterns
        py_files = list(find_files(self.project_dir, ["*.py"], ignore_patterns))
        
        all_imports = set()
        
        if py_files:
            self.console.print(f"Scanning {len(py_files)} Python files for imports...")
            
            for py_file in py_files:
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Extract import statements
                    import_lines = self._extract_imports(content)
                    all_imports.update(import_lines)
                    
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not read {py_file}: {e}[/yellow]")
            
            if all_imports:
                self.console.print(f"Found {len(all_imports)} unique import statements")
                
                # Use LLM to generate requirements.txt
                imports_text = "\n".join(sorted(all_imports))
                prompt = f"""Based on the following import statements from a Python project, generate a requirements.txt file with appropriate package versions.

Import statements found:
{imports_text}

Existing requirements.txt (if any):
{existing_dependencies}

Please generate a complete requirements.txt file that includes:
1. Only external packages (not built-in Python modules)
2. Reasonable version specifications (use >= for flexibility)
3. Common packages with their typical versions
4. Merge with existing requirements if provided

Return only the requirements.txt content, one package per line in format: package>=version
"""
                self.console.print("Generating requirements.txt...")
                generated_requirements = self.model_client.get_answer(prompt)
                
                # Clean the generated content
                generated_requirements = self._clean_requirements_content(generated_requirements)
                
            else:
                generated_requirements = "# No external imports found\n"
                if existing_dependencies:
                    generated_requirements = existing_dependencies
        else:
            generated_requirements = "# No Python files found\n"
            if existing_dependencies:
                generated_requirements = existing_dependencies
        
        # Save generated requirements.txt to output folder
        if self.output_dir:
            output_requirements_path = os.path.join(self.output_dir, "requirements.txt")
            with open(output_requirements_path, "w", encoding="utf-8") as f:
                f.write(generated_requirements)
            self.console.print(f"[green]✔ Generated requirements.txt saved to: {output_requirements_path}[/green]")
            
            # Also save dependency analysis information
            dependencies_info = f"""# Dependencies Analysis Report

## Existing requirements.txt:
{existing_dependencies if existing_dependencies else "None found"}

## Discovered imports ({len(all_imports)} unique):
{chr(10).join(sorted(all_imports)) if all_imports else "No imports found"}

## Generated requirements.txt:
{generated_requirements}
"""
            dependencies_analysis_path = os.path.join(self.output_dir, "dependencies_analysis.txt")
            with open(dependencies_analysis_path, "w", encoding="utf-8") as f:
                f.write(dependencies_info)
            self.console.print(f"[green]✔ Dependencies analysis saved to: {dependencies_analysis_path}[/green]")
        
        self.console.print("[green]✔ Project dependencies generated.[/green]")
        return generated_requirements
    
    def _extract_imports(self, content):
        """Extract import statements from Python code"""
        import re
        
        imports = set()
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comment lines
            if line.startswith('#') or not line:
                continue
            
            # Match import xxx format
            import_match = re.match(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', line)
            if import_match:
                imports.add(f"import {import_match.group(1)}")
                continue
            
            # Match from xxx import yyy format
            from_import_match = re.match(r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import\s+(.+)', line)
            if from_import_match:
                module = from_import_match.group(1)
                imports.add(f"from {module} import {from_import_match.group(2)}")
                continue
        
        return imports
    
    def _clean_requirements_content(self, content):
        """Clean generated requirements.txt content"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and obvious non-requirements format lines
            if not line or line.startswith('```') or line.startswith('Based on'):
                continue
                
            # If line contains package name and version info, keep it
            if '==' in line or '>=' in line or '<=' in line or '~=' in line or line.startswith('#'):
                cleaned_lines.append(line)
            elif re.match(r'^[a-zA-Z0-9_-]+$', line):
                # If only package name, add default version
                cleaned_lines.append(f"{line}>=1.0.0")
        
        return '\n'.join(cleaned_lines)

    def _generate_script_descriptions(self, max_workers=5):
        """
        Generate script descriptions using multithreading
        
        Args:
            max_workers (int): Maximum number of threads, default is 3
        """
        self.console.print("Generating script and document descriptions...")
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + gitignore_patterns
        # 将脚本模式和文档模式合并，以便生成更全面的文件描述
        all_patterns = SCRIPT_PATTERNS + DOCUMENT_PATTERNS
        filepaths = list(find_files(self.project_dir, all_patterns, ignore_patterns))

        if not filepaths:
            self.console.print("[yellow]No script or document files found to process.[/yellow]")
            return json.dumps({}, indent=2)

        table = Table(title="Files to be processed")
        table.add_column("File Path", style="cyan")
        for filepath in filepaths:
            table.add_row(os.path.relpath(filepath, self.project_dir))
        self.console.print(table)

        descriptions = {}
        descriptions_lock = Lock()  # Thread lock to protect shared dictionary
        
        def process_file(filepath):
            """Function to process a single file"""
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                prompt = f"Analyze the following script and provide a concise summary. Focus on:\n1. Main purpose and functionality\n2. Key functions/methods and their roles\n3. Important features or capabilities\n\nScript content:\n{content}"
                description = self.model_client.get_answer(prompt)
                
                # Use lock to protect shared resource
                with descriptions_lock:
                    descriptions[os.path.relpath(filepath, self.project_dir)] = description
                
                return True
            except Exception as e:
                self.console.print(f"[red]Error processing {filepath}: {e}[/red]")
                return False

        # Use thread pool for concurrent processing
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating...[/cyan]", total=len(filepaths))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_filepath = {
                    executor.submit(process_file, filepath): filepath 
                    for filepath in filepaths
                }
                
                # Process completed tasks
                for future in as_completed(future_to_filepath):
                    filepath = future_to_filepath[future]
                    try:
                        success = future.result()
                        if success:
                            self.console.print(f"[dim]✓ {os.path.relpath(filepath, self.project_dir)}[/dim]")
                        progress.update(task, advance=1)
                    except Exception as e:
                        self.console.print(f"[red]Exception for {filepath}: {e}[/red]")
                        progress.update(task, advance=1)

        # Save script descriptions to output folder
        descriptions_json = json.dumps(descriptions, indent=2, ensure_ascii=False)
        if self.output_dir:
            descriptions_path = os.path.join(self.output_dir, "script_descriptions.json")
            with open(descriptions_path, "w", encoding="utf-8") as f:
                f.write(descriptions_json)
            self.console.print(f"[green]✔ Script and document descriptions saved to: {descriptions_path}[/green]")
        
        self.console.print(f"[green]✔ Script and document descriptions generated using {max_workers} threads.[/green]")
        self.console.print(f"[green]✔ Processed {len(descriptions)} files successfully.[/green]")
        return descriptions_json

    def _generate_readme_content(
        self, structure, dependencies, descriptions, logo_path
    ):
        self.console.print("Generating README content...")
        try:
            template_path = get_readme_template_path()
            with open(template_path, "r") as f:
                template = f.read()
        except FileNotFoundError as e:
            self.console.print(f"[red]Error: {e}[/red]")
            return ""

        # Replace placeholders
        for key, value in self.config.items():
            if value:
                template = template.replace(f"{{{{{key}}}}}", value)
            else:
                # If value is empty, remove the line containing the placeholder
                template = re.sub(f".*{{{{{key}}}}}.*\n?", "", template)

        if self.config["github_username"] and self.config["repo_name"]:
            template = template.replace(
                "github_username/repo_name",
                f"{self.config['github_username']}/{self.config['repo_name']}",
            )
        else:
            # Remove all github-related badges and links if info is missing
            template = re.sub(
                r"\[\[(Contributors|Forks|Stargazers|Issues|project_license)-shield\]\]\[(Contributors|Forks|Stargazers|Issues|project_license)-url\]\n?",
                "",
                template,
            )

        if logo_path:
            # Logo 和 README 都在同一个输出目录中，使用相对路径
            relative_logo_path = os.path.relpath(logo_path, self.output_dir)
            template = template.replace("images/logo.png", relative_logo_path)
        else:
            template = re.sub(r'<img src="images/logo.png".*>', "", template)

        # Remove screenshot section
        template = re.sub(
            r"\[\[Product Name Screen Shot\]\[product-screenshot\]\]\(https://example.com\)",
            "",
            template,
        )
        template = re.sub(
            r"\[product-screenshot\]: images/screenshot.png", "", template
        )

        # Prepare additional project information for the prompt
        additional_info = ""
        if self.config.get("project_description"):
            additional_info += f"**Project Description:** {self.config['project_description']}\n"
        if self.config.get("entry_file"):
            additional_info += f"**Entry File:** {self.config['entry_file']}\n"
        if self.config.get("key_features"):
            additional_info += f"**Key Features:** {self.config['key_features']}\n"
        if self.config.get("additional_info"):
            additional_info += f"**Additional Information:** {self.config['additional_info']}\n"

        prompt = f"""You are a readme.md generator. You need to return the readme text directly without any other speech.
        Based on the following template, please generate a complete README.md file. 
        Fill in any missing information based on the project context provided.

        Use the additional project information provided by the user to enhance the content, especially for:
        - Project description and overview
        - Entry file information
        - Features section
        - Any additional information provided by the user

        **Template:**
        {template}

        **Project Structure:**
        ```
        {structure}
        ```

        **Dependencies:**
        ```
        {dependencies}
        ```

        **Script Descriptions:**
        {descriptions}

        **Additional Project Information:**
        {additional_info}

        Please ensure the final README is well-structured, professional, and incorporates all the user-provided information appropriately.
        """
        readme = self.model_client.get_answer(prompt)
        self.console.print("[green]✔ README content generated.[/green]")
        # Simple cleaning, remove ```readme``` and ```markdown```
        readme = readme.replace("```readme", "").replace("```markdown", "").strip("```")
        return readme
