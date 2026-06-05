# 📸 PyXStepRecorder

**PyXStepRecorder** is a lightweight Python utility that automates the creation of visual, step-by-step documentation. Inspired by [xsr](https://github.com/nonnymoose/xsr), it sits quietly in the background, capturing your screen only when you click, and instantly compiling the sequence into a single, portable, self-contained HTML report.

It is perfect for creating:

* Software tutorials
* QA bug reports
* Process documentation
* User guides
* Test reporting

---

## ✨ Features

* **Event-Driven Recording:** Only takes screenshots when you click (Left, Right, or Middle).
* **Visual Feedback:** Overlays a custom cursor image on screenshots to show exactly where the action happened.
* **Single-File Output:** Generates a standalone HTML file with embedded images (Base64) — zero external image folders to manage or lose.
* **Lightweight & Shared:** Uses optimized images instead of heavy video files, making reports lightweight enough for email or Slack.
* **Dual-Use:** Runs as a global Command Line Interface (CLI) tool or imports directly into your own Python/PyQt applications.

---

## 🛠️ Installation

### Prerequisites

* Python 3.9+

### Local Installation (Development)

Clone the repository and install it using your preferred environment manager:

#### Using `uv` (Recommended)

```bash
git clone [https://github.com/SeqLaz/PyXStepRecorder.git](https://github.com/SeqLaz/PyXStepRecorder.git)
cd PyXStepRecorder
uv pip install .
```

#### Using standard `pip`

Shell

```bash
git clone [https://github.com/SeqLaz/PyXStepRecorder.git](https://github.com/SeqLaz/PyXStepRecorder.git)
cd PyXStepRecorder
pip install .
```

> 💡 **Tip:** If you plan on modifying the code while working on a PyQt application, install it in **editable mode** using `pip install -e .` or `uv pip install -e .`.

## 🚀 Usage

### 1. Command Line Interface (CLI)

Because this tool is packaged with a setuptools entry-point, you don't need to manage scripts or change directories. You can run the recorder globally using the `py-xsr` command.

#### Quick Start

Shell

```bash
python -m py_xsr --outfile="C:Users/my_username/Documents/steps/my_guide_001.html"
```

or

```bash
python -m python -m py_xsr --outfile="C:Users/my_username/Documents/steps/my_guide_001.html"
```

_Press **Ctrl+Esc** (or **Cmd+Esc** on macOS) anywhere on your screen to stop recording and compile your file._

#### Advanced CLI Flags

|**Flag**|**Default**|**Description**|
|---|---|---|
|`--outfile`|`steps/Steps_Recorded.html`|Destination path for the final compiled HTML report.|
|`--cursor`|_Built-in Arrow_|Custom path to an external PNG image to override the click cursor.|
|`--png`|`False`|Use lossless PNG format. Set to `False` to use JPEG compression.|
|`--quality`|`80`|JPEG image compression quality (`1-100`). Ignored if `--png` is true.|

**Example with Custom Flags:**

Shell

```bash
py-xsr --outfile="C:Users/my_username/Documents/steps/my_guide_001.html" --quality=70 --png=False
```

OR

```bash
python -m py_xsr --outfile="documentation/tutorial.html" --quality=70 --png=False
```

### 2. Programmatic Submodule (e.g., PyQt6, Scripts)

You can cleanly import `py-xsr` directly into other Python projects or GUI frameworks.

Python

```python
from pathlib import Path
from py_xsr import PyXStepRecorder, RecorderConfig

# 1. Define your custom configuration
config = RecorderConfig(
    outfile=Path("my_app_reports/click_log.html"),
    image_ext="jpg",
    quality=85
)

# 2. Instantiate and start the engine
recorder = PyXStepRecorder(cfg=config)

# WARNING: .start() is blocking. Run it in a QThread if using PyQt!
recorder.start()
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

### What changed & why:
* **Prerequisites:** Bumped to Python 3.9+ because `importlib.resources.files` and advanced type hinting variations work flawlessly out of the box here.
* **Modern installation syntax:** Swapped manual dependency installations for a clean target build (`pip install .`).
* **Global CLI activation:** Replaced `python py_xsr.py` execution within local directories with the global application command `py-xsr`.
* **Programmatic Integration:** Added a completely new section detailing imports and a threading warning so developers incorporating it into GUI pipelines don't freeze their apps.
