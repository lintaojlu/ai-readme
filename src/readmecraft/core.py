import os
import json
import re
import subprocess
from rich.console import Console
import drawsvg as draw
from rich.progress import Progress
from rich.table import Table
from readmecraft.utils.llm import LLM
from readmecraft.utils.file_handler import find_files, get_project_structure, load_gitignore_patterns
from readmecraft.utils.logo_generator import generate_logo
from .config import DEFAULT_IGNORE_PATTERNS, SCRIPT_PATTERNS, get_readme_template_path

class ReadmeCraft:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.llm = LLM()
        self.console = Console()
        self.config = {
            "github_username": "",
            "repo_name": "",
            "twitter_handle": "",
            "linkedin_username": "",
            "email": "",
        }

    def generate(self):
        self.console.print("[bold green]Generating README...[/bold green]")
        self._get_git_info()
        self._get_user_info()
        
        structure = self._generate_project_structure()
        dependencies = self._generate_project_dependencies()
        descriptions = self._generate_script_descriptions()
        logo_path = generate_logo(self.project_dir, self.config.get("repo_name", "Logo"), descriptions, self.llm, self.console)

        readme_content = self._generate_readme_content(
            structure, dependencies, descriptions, logo_path
        )

        with open(os.path.join(self.project_dir, "README.md"), "w") as f:
            f.write(readme_content)
        
        self.console.print("[bold green]README.md generated successfully.[/bold green]")

    def _get_git_info(self):
        self.console.print("Gathering Git information...")
        try:
            git_config_path = os.path.join(self.project_dir, ".git", "config")
            if os.path.exists(git_config_path):
                with open(git_config_path, "r") as f:
                    config_content = f.read()
                url_match = re.search(r'url =.*github.com[:/](.*?)/(.*?).git', config_content)
                if url_match:
                    self.config["github_username"] = url_match.group(1)
                    self.config["repo_name"] = url_match.group(2)
                    self.console.print("[green]✔ Git information gathered.[/green]")
                    return
        except Exception as e:
            self.console.print(f"[yellow]Could not read .git/config: {e}[/yellow]")

        self.console.print("[yellow]Git info not found, please enter manually (or press Enter to skip):[/yellow]")
        self.config["github_username"] = self.console.input("GitHub Username: ")
        self.config["repo_name"] = self.console.input("Repository Name: ")

    def _get_user_info(self):
        self.console.print("Please enter your contact information (or press Enter to skip):")
        self.config["twitter_handle"] = self.console.input("Twitter Handle: ")
        self.config["linkedin_username"] = self.console.input("LinkedIn Username: ")
        self.config["email"] = self.console.input("Email: ")




    def _generate_project_structure(self):
        self.console.print("Generating project structure...")
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + gitignore_patterns
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
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + gitignore_patterns
        filepaths = list(find_files(self.project_dir, SCRIPT_PATTERNS, ignore_patterns))

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

    def _generate_readme_content(self, structure, dependencies, descriptions, logo_path):
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
            template = template.replace("github_username/repo_name", f"{self.config['github_username']}/{self.config['repo_name']}")
        else:
            # Remove all github-related badges and links if info is missing
            template = re.sub(r'\[\[(Contributors|Forks|Stargazers|Issues|project_license)-shield\]\]\[(Contributors|Forks|Stargazers|Issues|project_license)-url\]\n?', '', template)

        if logo_path:
            template = template.replace('images/logo.png', os.path.relpath(logo_path, self.project_dir))
        else:
            template = re.sub(r'<img src="images/logo.png".*>', '', template)

        # Remove screenshot section
        template = re.sub(r'\[\[Product Name Screen Shot\]\[product-screenshot\]\]\(https://example.com\)', '', template)
        template = re.sub(r'\[product-screenshot\]: images/screenshot.png', '', template)

        prompt = f"""You are a readme.md generator. You need to return the readme text directly without any other speech.
        Based on the following template, please generate a complete README.md file. 
        Fill in the `project_title`, `project_description`, and `project_license` (e.g., MIT, Apache 2.0) based on the project context provided.
        Also, complete the 'Built With' section based on the dependencies.

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

        Please ensure the final README is well-structured, professional, and ready to use.
        """
        messages = [{"role": "user", "content": prompt}]
        readme = self.llm.get_answer(messages)
        self.console.print("[green]✔ README content generated.[/green]")
        return readme