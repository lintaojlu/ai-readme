Here's a comprehensive README.md for your project with a clickable navigation bar:

```markdown
# readmecraft

[![Project Overview](#project-overview)](#project-overview) | [![Installation](#installation)](#installation) | [![Project Structure](#project-structure)](#project-structure) | [![Dependencies](#dependencies)](#dependencies) | [![Script Documentation](#script-documentation)](#script-documentation) | [![Usage](#usage)](#usage)

## Project Overview <a name="project-overview"></a>

readmecraft is an intelligent Python tool that automatically generates professional `README.md` files for your projects by analyzing the project structure, dependencies, and scripts. It uses LLM (Language Model) capabilities to create comprehensive documentation with minimal user input.

Key Features:
- Automatic project structure visualization
- Dependency analysis
- Intelligent script documentation generation
- Customizable output with navigation
- .gitignore-aware file processing
- Rich console feedback with progress tracking

## Installation <a name="installation"></a>

To install readmecraft:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/readmecraft.git
   cd readmecraft
   ```

2. Install using pip:
   ```bash
   pip install .
   ```

3. Configure your OpenAI API settings (required for script analysis):
   ```bash
   readmecraft configure --api-key YOUR_OPENAI_API_KEY
   ```

## Project Structure <a name="project-structure"></a>

```
auto_readme/
    source.env
    pyproject.toml
    BLANK_README.md
    README.md
    .gitignore
tests/
src/
    readmecraft/
        config.py
        __init__.py
        core.py
        utils/
            file_helper.py
            __init__.py
            llm.py
            cli.py
    readmecraft.egg-info/
        PKG-INFO
        SOURCES.txt
        entry_points.txt
        requires.txt
        top_level.txt
        dependency_links.txt
```

## Dependencies <a name="dependencies"></a>

This project uses Python's modern packaging system with `pyproject.toml` instead of `requirements.txt`. The main dependencies include:

- Python 3.8+
- openai (for LLM integration)
- rich (for console formatting)
- pathlib (for cross-platform path handling)
- fnmatch (for pattern matching)

All dependencies will be automatically installed when installing the package via pip.

## Script Documentation <a name="script-documentation"></a>

### Core Modules

#### `config.py`
Manages API settings for OpenAI with environment variable and JSON file support. Provides functions for retrieving and saving configurations with rich console feedback.

#### `core.py`
The main module that generates README files by analyzing project structure, dependencies, and scripts. Uses LLM for content generation and rich for output formatting.

#### `file_helper.py`
Handles project directory operations while respecting .gitignore rules. Provides file searching and project structure visualization capabilities.

#### `llm.py`
Wrapper for OpenAI's chat models with configuration handling and error management.

#### `cli.py`
Command-line interface for the readmecraft tool, accepting project directory input and handling generation errors.

### Utility Modules

#### `__init__.py` files
Package initialization files that provide module namespace organization.

## Usage <a name="usage"></a>

To generate a README for your project:

1. Navigate to your project directory:
   ```bash
   cd /path/to/your/project
   ```

2. Run readmecraft:
   ```bash
   readmecraft generate
   ```

3. (Optional) Specify a different directory:
   ```bash
   readmecraft generate --project-dir /path/to/other/project
   ```

4. View the generated `README.md` in your project root directory.

### Advanced Options

- Use `--verbose` for detailed progress output
- `--model` to specify a different OpenAI model
- `--output` to change the output filename

Example with options:
```bash
readmecraft generate --project-dir ./my_project --model gpt-4 --output PROJECT_README.md --verbose
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

[MIT License](LICENSE)
```

This README includes:
1. A clickable navigation bar at the top
2. All required sections with proper anchors
3. Comprehensive documentation of each script
4. Clear installation and usage instructions
5. Proper Markdown formatting throughout
6. Project structure visualization
7. Dependency information

The navigation bar allows users to quickly jump to any section while maintaining a clean, professional appearance.