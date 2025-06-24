
<div align="center">
  <svg width="200" height="80" viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="40" height="40" rx="5" fill="#4F46E5"/>
  <path d="M80 30 L160 30 L160 50 L80 50 Z" fill="none" stroke="#4F46E5" stroke-width="4" stroke-linecap="round"/>
  <path d="M80 40 L120 40" stroke="#4F46E5" stroke-width="4" stroke-linecap="round"/>
  <path d="M140 40 L160 40" stroke="#4F46E5" stroke-width="4" stroke-linecap="round"/>
  <circle cx="180" cy="40" r="10" fill="#4F46E5"/>
</svg>
  <h3 align="center">ReadmeCraft</h3>
  <p align="center">
    An AI-powered tool for automatically generating professional README.md files for your projects.
    <br />
    ·
    ·
  </p>
</div>

---

## About The Project

ReadmeCraft is a Python-based tool that automates the creation of comprehensive README.md files for software projects. It analyzes your project structure, dependencies, and scripts to generate polished documentation with minimal effort. Key features include:

- **Project Analysis**: Scans your project directory to understand its structure and components
- **AI-Powered Descriptions**: Uses LLMs to generate meaningful descriptions for your scripts
- **Dynamic README Generation**: Populates a professional template with project-specific details
- **Logo Generation**: Creates minimalist SVG logos for your project documentation

## Built With

- Python
- OpenAI API (for LLM integration)
- Rich (for console output formatting)
- Pytest (for testing)

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for full functionality)
- Git (for repository information extraction)

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/your_username/readmecraft.git
   ```
2. Install dependencies
   ```sh
   pip install -e .
   ```
3. Configure your OpenAI API key
   ```sh
   export OPENAI_API_KEY='your-api-key'
   ```

## Usage

Run the following command in your project directory:
```sh
python -m readmecraft.utils.cli /path/to/your/project
```

The tool will:
1. Analyze your project structure
2. Generate script descriptions
3. Create a professional README.md file
4. Optionally generate a project logo

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - your.email@example.com

Project Link: [https://github.com/your_username/readmecraft](https://github.com/your_username/readmecraft)

## Acknowledgments

* [OpenAI](https://openai.com)
* [Rich](https://github.com/Textualize/rich)
* [Python](https://www.python.org)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/your_username/readmecraft.svg?style=for-the-badge
[contributors-url]: https://github.com/your_username/readmecraft/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/your_username/readmecraft.svg?style=for-the-badge
[forks-url]: https://github.com/your_username/readmecraft/network/members
[stars-shield]: https://img.shields.io/github/stars/your_username/readmecraft.svg?style=for-the-badge
[stars-url]: https://github.com/your_username/readmecraft/stargazers
[issues-shield]: https://img.shields.io/github/issues/your_username/readmecraft.svg?style=for-the-badge
[issues-url]: https://github.com/your_username/readmecraft/issues
[license-shield]: https://img.shields.io/github/license/your_username/readmecraft.svg?style=for-the-badge
[license-url]: https://github.com/your_username/readmecraft/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/your_username
