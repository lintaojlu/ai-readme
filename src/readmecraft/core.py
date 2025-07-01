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
from .config import DEFAULT_IGNORE_PATTERNS, SCRIPT_PATTERNS, get_readme_template_path


class ReadmeCraft:
    def __init__(self, project_dir=None):
        self.model_client = ModelClient()
        self.console = Console()
        self.project_dir = project_dir  # 初始化时设置项目目录
        self.output_dir = None  # 输出目录将在 _get_basic_info 中设置
        self.config = {
            "github_username": "",
            "repo_name": "",
            "twitter_handle": "",
            "linkedin_username": "",
            "email": "",
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

        # 将 README.md 保存到输出目录
        readme_path = os.path.join(self.output_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        self.console.print(
            f"[bold green]✔ README.md 已生成到: {readme_path}[/bold green]"
        )
        if logo_path:
            self.console.print(f"[bold green]✔ Logo 已生成到: {logo_path}[/bold green]")
        self.console.print(
            f"[bold green]✔ 所有文件已保存到输出目录: {self.output_dir}[/bold green]"
        )

    def _get_basic_info(self):
        """
        交互式获取基本信息：项目路径和输出目录
        """
        self.console.print("[bold cyan]ReadmeCraft - AI README 生成器[/bold cyan]")
        self.console.print("请配置基本信息（按 Enter 使用默认值）\n")

        # 获取项目路径
        current_dir = os.getcwd()
        project_input = self.console.input(
            f"[cyan]项目路径[/cyan] (默认: {current_dir}): "
        ).strip()

        if project_input:
            # 处理相对路径和绝对路径
            if os.path.isabs(project_input):
                self.project_dir = project_input
            else:
                self.project_dir = os.path.join(current_dir, project_input)
        else:
            self.project_dir = current_dir

        # 检查项目路径是否存在
        if not os.path.exists(self.project_dir):
            self.console.print(f"[red]错误: 项目路径 '{self.project_dir}' 不存在[/red]")
            exit(1)

        self.console.print(f"[green]✔ 项目路径: {self.project_dir}[/green]")

        # 获取输出目录
        output_input = self.console.input(
            f"[cyan]输出目录[/cyan] (默认: {current_dir}): "
        ).strip()

        if output_input:
            # 处理相对路径和绝对路径
            if os.path.isabs(output_input):
                output_base = output_input
            else:
                output_base = os.path.join(current_dir, output_input)
        else:
            output_base = current_dir

        # 在输出目录下创建 aireadme_output 子目录
        self.output_dir = os.path.join(output_base, "aireadme_output")

        # 创建输出目录
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            self.console.print(f"[green]✔ 输出目录: {self.output_dir}[/green]")
        except Exception as e:
            self.console.print(
                f"[red]错误: 无法创建输出目录 '{self.output_dir}': {e}[/red]"
            )
            exit(1)

        self.console.print()  # 空行分隔

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
                    return
        except Exception as e:
            self.console.print(f"[yellow]Could not read .git/config: {e}[/yellow]")

        self.console.print(
            "[yellow]Git info not found, please enter manually (or press Enter to skip):[/yellow]"
        )
        self.config["github_username"] = self.console.input("GitHub Username: ")
        self.config["repo_name"] = self.console.input("Repository Name: ")

    def _get_user_info(self):
        self.console.print(
            "Please enter your contact information (or press Enter to skip):"
        )
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

    def _generate_script_descriptions(self, max_workers=3):
        """
        使用多线程并发生成脚本描述
        
        Args:
            max_workers (int): 最大线程数，默认为3
        """
        self.console.print("Generating script descriptions...")
        gitignore_patterns = load_gitignore_patterns(self.project_dir)
        ignore_patterns = DEFAULT_IGNORE_PATTERNS + gitignore_patterns
        filepaths = list(find_files(self.project_dir, SCRIPT_PATTERNS, ignore_patterns))

        if not filepaths:
            self.console.print("[yellow]No script files found to process.[/yellow]")
            return json.dumps({}, indent=2)

        table = Table(title="Files to be processed")
        table.add_column("File Path", style="cyan")
        for filepath in filepaths:
            table.add_row(os.path.relpath(filepath, self.project_dir))
        self.console.print(table)

        descriptions = {}
        descriptions_lock = Lock()  # 保护共享字典的线程锁
        
        def process_file(filepath):
            """处理单个文件的函数"""
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                prompt = f"Please provide a brief description of the following script:\n\n{content}"
                description = self.model_client.get_answer(prompt)
                
                # 使用锁保护共享资源
                with descriptions_lock:
                    descriptions[os.path.relpath(filepath, self.project_dir)] = description
                
                return True
            except Exception as e:
                self.console.print(f"[red]Error processing {filepath}: {e}[/red]")
                return False

        # 使用线程池执行并发处理
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating...[/cyan]", total=len(filepaths))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_filepath = {
                    executor.submit(process_file, filepath): filepath 
                    for filepath in filepaths
                }
                
                # 处理完成的任务
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

        self.console.print(f"[green]✔ Script descriptions generated using {max_workers} threads.[/green]")
        self.console.print(f"[green]✔ Processed {len(descriptions)} files successfully.[/green]")
        return json.dumps(descriptions, indent=2)

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
        readme = self.model_client.get_answer(prompt)
        self.console.print("[green]✔ README content generated.[/green]")
        # 进行简单清洗，删除掉```readme```和```markdown```
        readme = readme.replace("```readme", "").replace("```markdown", "").strip("```")
        return readme
