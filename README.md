# AutoReadme

## 项目简介

AutoReadme 是一个自动化工具，旨在为给定的项目目录生成 README 文件和相关依赖项（例如项目结构和 `requirements.txt`）。它通过分析项目目录、文件结构和依赖关系，自动生成详细的项目文档，减少人工干预。对于任何未知信息，工具将使用占位符 (`<>`) 填充。

## 配置

AutoReadme 需要在 `config` 目录下提供一个 `llm_config.json` 配置文件。该文件包含语言模型所需的 API 密钥及其他参数设置。

示例 `llm_config.json` 文件：

```json
{
  "OPENAI_CONFIG": {
    "OPENAI_KEYS_BASES": [
      {
        "OPENAI_KEY": "<your_openai_key>",
        "OPENAI_BASE": "<your_openai_base>"
      }
    ],
    "OPENAI_MAX_TOKENS": 1000,
    "OPENAI_TEMPERATURE": 0.7
  }
}
```

## 安装方法

请按照以下步骤安装和设置 AutoReadme：

1. 克隆此仓库：
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. 创建并激活虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows 用户请使用 `venv\Scripts\activate`
   ```

3. 安装所需依赖项：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

可以通过运行 `auto_readme.py` 脚本并传递必要的命令行参数来使用 AutoReadme。以下是一个示例：

```bash
python auto_readme.py --project_name <Project_Name> --project_dir <Project_Directory> --project_description <Project_Description> --project_author <Author_Name>
```

Python 代码示例：

```python
from auto_readme import AutoReadme

auto_readme = AutoReadme(
    project_name="MyProject",
    project_dir="./",
    project_description="This is my project.",
    project_author="Your Name"
)
auto_readme.generate_readme()
```

## 输出

项目的预期输出包括：

- 在指定输出目录下生成的 `README.md` 文件。
- 描述项目结构的 `PROJECT_STRUCTURE.md` 文件。
- 列出项目依赖项的 `requirements.txt` 文件。
- 脚本描述的 JSON 格式文件。

## 贡献指南

欢迎对 AutoReadme 项目进行贡献！请遵循以下步骤：

1. Fork 本仓库。
2. 创建一个新的分支：
   ```bash
   git checkout -b feature/my-feature
   ```
3. 提交您的更改：
   ```bash
   git commit -m "Add new feature"
   ```
4. 推送到分支：
   ```bash
   git push origin feature/my-feature
   ```
5. 创建一个详细描述您更改的 Pull Request。

请遵循以下编码标准：

- 编写清晰简洁的提交信息。
- 遵循 PEP 8 Python 编码规范。
- 确保您的代码通过所有测试。

## 许可证

此项目基于 MIT 许可证发布。

## 联系方式

如需帮助或有任何疑问，请联系项目维护者：

- Lin Tao: lint22@mails.tsinghua.edu.cn

感谢您对 AutoReadme 项目的关注和支持！