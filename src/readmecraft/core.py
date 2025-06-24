import os
import json
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from readmecraft.utils.llm import LLM
from readmecraft.utils.file_helper import find_files, get_project_structure, load_gitignore_patterns

class readmecraft:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.llm = LLM()
        self.console = Console()

    def generate(self):
        self.console.print("[bold green]Generating README...[/bold green]")
        structure = self._generate_project_structure()
        dependencies = self._generate_project_dependencies()
        descriptions = self._generate_script_descriptions()

        readme_content = self._generate_readme_content(
            structure, dependencies, descriptions
        )

        with open(os.path.join(self.project_dir, "README.md"), "w") as f:
            f.write(readme_content)
        
        self.console.print("[bold green]README.md generated successfully.[/bold green]")

    def _generate_project_structure(self):
        self.console.print("Generating project structure...")
        default_ignore = [".git", ".vscode", "__pycache__", "*.pyc", ".DS_Store"]
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = default_ignore + gitignore_patterns
        structure = get_project_structure(self.project_dir, ignore_patterns)
        self.console.print("[green]✔ Project structure generated.[/green]")
        return structure

    def _generate_project_dependencies(self):
        self.console.print("Generating project dependencies...")
        requirements_path = os.path.join(self.project_dir, "requirements.txt")
        dependencies = "No requirements.txt found."
        if os.path.exists(requirements_path):
            with open(requirements_path, "r") as f:
                dependencies = f.read()
        self.console.print("[green]✔ Project dependencies generated.[/green]")
        return dependencies

    def _generate_script_descriptions(self):
        self.console.print("Generating script descriptions...")
        script_patterns = ["*.py", "*.sh"]
        default_ignore = [".git", ".vscode", "__pycache__", "*.pyc", ".DS_Store"]
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = default_ignore + gitignore_patterns
        filepaths = list(find_files(self.project_dir, script_patterns, ignore_patterns))

        table = Table(title="Files to be processed")
        table.add_column("File Path", style="cyan")
        for filepath in filepaths:
            table.add_row(os.path.relpath(filepath, self.project_dir))
        self.console.print(table)

        descriptions = {}
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating...[/cyan]", total=len(filepaths))
            for filepath in filepaths:
                with open(filepath, "r") as f:
                    content = f.read()
                prompt = f"Please provide a brief description of the following script:\n\n{content}"
                messages = [{"role": "user", "content": prompt}]
                description = self.llm.get_answer(messages)
                descriptions[os.path.relpath(filepath, self.project_dir)] = description
                progress.update(task, advance=1)
        
        self.console.print("[green]✔ Script descriptions generated.[/green]")
        return json.dumps(descriptions, indent=2)

    def _generate_readme_content(self, structure, dependencies, descriptions):
        prompt = f"""
        Please generate a README.md for a project with the following details. The README should include a clickable navigation bar at the top that allows users to quickly jump to different sections:

        **Project Structure:**
        {structure}

        **Dependencies:**
        {dependencies}

        **Script Descriptions:**
        {descriptions}

        Requirements for the README:
        1. Start with a navigation bar at the top containing links to all major sections
        2. Each section should have a proper heading with an anchor that can be linked to
        3. The navigation bar should use markdown link syntax like [Section Name](#section-name)
        4. Include at least these sections in the navigation:
           - Project Overview
           - Installation
           - Project Structure
           - Dependencies
           - Script Documentation
           - Usage
        5. The README should be comprehensive and well-structured
        6. Use proper markdown formatting throughout the document
        """
        messages = [{"role": "user", "content": prompt}]
        return self.llm.get_answer(messages)