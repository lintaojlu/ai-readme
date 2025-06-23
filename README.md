# AutoReadme

AutoReadme is a Python tool that automatically generates comprehensive `README.md` files for your projects by analyzing the project structure, dependencies, and source code files. It leverages LLM (Large Language Model) capabilities to generate meaningful descriptions of your scripts and organizes all information into a professional README format.

## Features

- **Automatic Project Structure Analysis**: Scans your project directory and generates a structured overview
- **Dependency Detection**: Identifies and includes project dependencies
- **AI-Powered Descriptions**: Uses LLM to generate clear descriptions of your scripts
- **Gitignore Support**: Respects `.gitignore` rules when scanning your project
- **CLI Interface**: Simple command-line interface for easy integration into your workflow
- **Configuration Management**: Supports both environment variables and config file for API settings

## Installation

Since there's no `requirements.txt` file, you'll need to install the package directly. First, ensure you have Python 3.7+ installed, then:

```bash
pip install -e .
```

Or if you want to install it in development mode:

```bash
pip install -e /path/to/auto_readme
```

## Configuration

AutoReadme requires configuration for the LLM (likely OpenAI) API. You can configure it in two ways:

1. **Environment Variables**:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   export OPENAI_BASE_URL='https://api.openai.com/v1'  # Optional
   export MODEL_NAME='gpt-4o'  # Optional, defaults to gpt-4o
   ```

2. **Config File**:
   The tool will automatically create and use a config file at `~/.config/autoreadme/user_config.json` if you prefer file-based configuration.

## Usage

Run AutoReadme from the command line:

```bash
autoreadme [project_dir]
```

Where `[project_dir]` is optional and defaults to the current working directory.

### Example

```bash
# Generate README for current directory
autoreadme

# Generate README for specific project
autoreadme /path/to/your/project
```

## Project Structure

```
auto_readme/
    pyproject.toml
    .gitignore
src/
    autoreadme/
        config.py          # Configuration management
        __init__.py        # Package initialization
        llm.py             # LLM interface
        core.py            # Main README generation logic
        cli.py             # Command-line interface
        utils/
            file_helper.py # File operations and gitignore handling
            __init__.py   # Utilities package initialization
    autoreadme.egg-info/   # Package metadata
```

## Script Descriptions

### `config.py`
Manages configuration settings with the following features:
- Checks for environment variables first (OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME)
- Falls back to reading from a JSON config file if environment variables aren't set
- Provides functions to save and retrieve configuration

### `llm.py`
Provides a simple interface for interacting with OpenAI's chat models:
- Loads configuration to create an OpenAI client instance
- Defaults to "gpt-4o" model if none is specified
- Provides a `get_answer()` method for chat completions with basic error handling

### `core.py`
Main `AutoReadme` class that generates README files:
- Scans project directory (respecting .gitignore)
- Extracts dependencies
- Uses LLM to generate script descriptions
- Combines all information into a well-structured README.md
- Uses `rich` library for formatted console output

### `cli.py`
Command-line interface for the tool:
- Accepts optional project directory argument
- Wraps the `AutoReadme` class functionality
- Provides basic error handling and user feedback

### `utils/file_helper.py`
File operations utilities:
- Reads and parses `.gitignore` files
- Checks if paths should be ignored
- Recursively searches directories while respecting ignore rules
- Generates tree-like project structure representations

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

[MIT License](LICENSE) (Note: You may want to add a proper license file to your project)