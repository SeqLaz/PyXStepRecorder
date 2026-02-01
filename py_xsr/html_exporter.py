from dataclasses import dataclass
import base64
import html
from pathlib import Path


@dataclass
class GenerateReport:
    """
    Generates a standalone HTML report containing a sequence of steps and embedded screenshots.

    This class takes a list of step objects and a directory of images, encodes the
    images into Base64, and embeds them directly into a single HTML file for easy sharing.

    Attributes:
        title (str): The display title of the HTML report.
        outfile (Path): The destination file path where the HTML report will be saved.
        steps (list): A list of objects representing the report steps. Each object
            must strictly possess `.description` (str) and `.image_filename` (str) attributes.
        temp_dir (Path): The directory path containing the source screenshot images.
        image_ext (str): The file extension of the source images (e.g., 'png', 'jpg')
            used to determine the MIME type during encoding.
    """

    title: str
    outfile: Path
    steps: list
    temp_dir: Path
    image_ext: str

    def get_b64(self, filename):
        """
        Reads an image file from the temporary directory and converts it to a Base64 data URI.

        This method validates that the file exists before attempting to read it.
        It constructs the MIME type based on the class `image_ext` attribute.

        Args:
            filename (str): The name of the image file (e.g., "screenshot_01.png").
                If None or empty, returns an empty string.

        Returns:
            str: A formatted data URI string (e.g., "data:image/png;base64,...") ready
            for use in an HTML `<img>` src attribute. Returns an empty string if
            the file does not exist.
        """
        if not filename:
            return ""
        path = self.temp_dir / filename
        if not path.exists():
            return ""
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            mime = "image/png" if self.image_ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{encoded}"

    def generate_report(self):
        """
        Generates the HTML report with a modern, card-based UI.
        """
        print("Generating HTML Report...")

        if self.outfile.parent:
            self.outfile.parent.mkdir(parents=True, exist_ok=True)

        html_parts = [
            f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>{html.escape(self.title)}</title>
                <link
                href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap"
                rel="stylesheet"
                />
                <style>
                :root {{
                    --bg-color: #f3f4f6;
                    --card-bg: #ffffff;
                    --text-main: #111827;
                    --text-sub: #6b7280;
                    --accent-color: #3b82f6;
                    --border-color: #e5e7eb;
                }}
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    background-color: var(--bg-color);
                    color: var(--text-main);
                    margin: 0;
                    padding: 40px 20px;
                    line-height: 1.6;
                }}
                .container {{
                    margin: 0 auto;
                }}
                header {{
                    text-align: center;
                    margin-bottom: 60px;
                }}
                h1 {{
                    font-size: 2.5rem;
                    font-weight: 800;
                    margin: 0 0 10px 0;
                    letter-spacing: -0.05rem;
                    color: var(--text-main);
                }}
                .step-card {{
                    background: var(--card-bg);
                    border-radius: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    margin-bottom: 40px;
                    overflow: hidden;
                    border: 1px solid var(--border-color);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }}
                .step-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                }}
                .step-header {{
                    padding: 20px 24px;
                    border-bottom: 1px solid var(--border-color);
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    background: #f9fafb;
                }}
                .step-badge {{
                    background-color: var(--accent-color);
                    color: white;
                    font-weight: 700;
                    font-size: 0.85rem;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }}
                .step-title {{
                    font-weight: 600;
                    font-size: 1.1rem;
                    color: #374151;
                }}
                .step-image-container {{
                    background-color: #000;
                    display: flex;
                    justify-content: center;
                }}
                img {{
                    display: block;
                    max-width: 100%;
                    height: auto;
                    opacity: 0.98;
                }}
                </style>
            </head>
            <body>
                <div class="container">
                <header>
                    <h1>{html.escape(self.title)}</h1>
                </header>
            """
        ]

        for i, step in enumerate(self.steps, 1):
            img_tag = ""
            if step.image_filename:
                b64_src = self.get_b64(step.image_filename)
                img_tag = f'<div class="step-image-container"><img src="{b64_src}" loading="lazy" /></div>'

            html_parts.append(f"""
            <div class="step-card">
                <div class="step-header">
                    <div class="step-badge">{i}</div>
                    <div class="step-title">{html.escape(step.description)}</div>
                </div>
                {img_tag}
            </div>""")

        html_parts.append("""
            </div>
        </body>
        </html>
        """)

        with open(self.outfile, "w", encoding="utf-8") as html_file:
            html_file.write("".join(html_parts))

        print(f"Saved to: {str(self.outfile)}")
