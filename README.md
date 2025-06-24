
<p align="center">
  <img src="images/logo.png" alt="logo" width="200"/>
</p>
<h3 align="center">ReadmeCraft</h3>
<p align="center">
  An automated README.md generator that creates professional documentation for your projects with AI assistance.
  <br />
  ·
  ·
</p>
</div>

---

## About The Project

ReadmeCraft is a Python-based tool that automatically generates comprehensive `README.md` files for software projects. It analyzes project structure, dependencies, and scripts to create professional documentation with minimal user input. The tool leverages AI to generate descriptions, create project logos, and format content according to best practices.

Key features:
- Automatic project structure analysis
- AI-powered script descriptions
- Dependency detection
- Logo generation
- Git integration
- Customizable templates

## Built With

- Python
- cairosvg (for SVG to PNG conversion)
- Rich (for console formatting)
- OpenAI API (for AI-powered content generation)

## Getting Started

### Prerequisites

- Python 3.7+
- OpenAI API key (for AI features)
- cairosvg dependencies (libcairo2 on Linux)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your_username/readmecraft.git
   ```
2. Install dependencies:
   ```sh
   pip install -e .
   ```
3. Set up your OpenAI API key:
   ```sh
   export OPENAI_API_KEY='your-api-key'
   ```

## Usage

Run the tool from the command line:
```sh
python -m readmecraft.utils.cli /path/to/your/project
```

The tool will:
1. Analyze your project structure
2. Generate a logo
3. Create a comprehensive README.md file

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

* [cairosvg](https://cairosvg.org/)
* [Rich](https://github.com/Textualize/rich)
* [OpenAI](https://openai.com/)

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
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
