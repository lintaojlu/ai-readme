import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
from readmecraft.utils.logo_generator import generate_logo

class TestLogoGenerator(unittest.TestCase):

    def setUp(self):
        self.project_dir = "/tmp/test_project"
        # Use a temporary directory for test artifacts
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)
        self.repo_name = "test_repo"
        self.descriptions = "This is a test project."

        self.llm = MagicMock()
        self.console = MagicMock()

    def tearDown(self):
        images_dir = os.path.join(self.project_dir, "images")
        logo_path = os.path.join(images_dir, "logo.png")
        if os.path.exists(logo_path):
            os.remove(logo_path)
        if os.path.exists(images_dir):
            os.rmdir(images_dir)
        if os.path.exists(self.project_dir):
            os.rmdir(self.project_dir)

    @patch('requests.post')
    def test_generate_logo_success(self, mock_post):
        # Mock LLM to return drawio XML
        self.llm.get_answer.return_value = "<mxGraphModel>...</mxGraphModel>"
        
        # Mock requests.post response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_png_content'
        mock_post.return_value = mock_response

        logo_path = generate_logo(self.project_dir, self.repo_name, self.descriptions, self.llm, self.console)

        self.assertIsNotNone(logo_path)
        self.assertTrue(os.path.exists(logo_path))
        with open(logo_path, 'rb') as f:
            self.assertEqual(f.read(), b'fake_png_content')
        
        self.llm.get_answer.assert_called_once()
        mock_post.assert_called_once()
        self.console.print.assert_any_call("Generating project logo...")
        self.console.print.assert_any_call(f"[green]✔ Logo generated from drawio and saved at {logo_path}[/green]")

    @patch('requests.post')
    @patch('drawsvg.Drawing')
    def test_generate_logo_fallback(self, mock_drawing, mock_post):
        # Mock LLM to return drawio XML
        self.llm.get_answer.return_value = "<mxGraphModel>...</mxGraphModel>"
        
        # Mock requests.post to simulate a failure
        mock_post.side_effect = Exception("Failed to connect")

        # Mock the drawsvg part for fallback
        mock_svg = MagicMock()
        mock_drawing.return_value = mock_svg

        def save_png_side_effect(path):
            # Simulate file creation
            with open(path, 'w') as f:
                f.write("fake placeholder")

        mock_svg.save_png.side_effect = save_png_side_effect

        logo_path = generate_logo(self.project_dir, self.repo_name, self.descriptions, self.llm, self.console)

        self.assertIsNotNone(logo_path)
        self.assertTrue(os.path.exists(logo_path))

        self.llm.get_answer.assert_called_once()
        mock_post.assert_called_once()
        mock_svg.save_png.assert_called_with(logo_path)
        self.console.print.assert_any_call("Generating project logo...")
        self.console.print.assert_any_call("[red]Failed to convert drawio to png: Failed to connect[/red]")
        self.console.print.assert_any_call("Generating placeholder logo as a fallback...")
        self.console.print.assert_any_call(f"[green]✔ Placeholder logo generated at {logo_path}[/green]")

if __name__ == '__main__':
    unittest.main()