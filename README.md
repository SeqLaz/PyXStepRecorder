# 📸 PyXStepRecorder

**PyXStepRecorder**  is a lightweight Python tool that automates the creation of visual, step-by-step documentation.
Inspired by [xsr](https://github.com/nonnymoose/xsr), it sits quietly in the background, capturing your screen only when you click,
and instantly compiling everything into a single, portable HTML file.

It is perfect for creating:

* Software tutorials
* QA bug reports
* Process documentation
* User guides
* Tests reports

---

## ✨ Features

* **Event-Driven Recording:** Only takes screenshots when you click (Left, Right, or Middle).
* **Visual Feedback:** Overlays a custom cursor image on screenshots to show exactly where you clicked.
* **Single-File Output:** Generates a standalone HTML file with embedded images (Base64) — no external image folders to manage.
* **Lightweight:** Uses static images instead of video, making files small and easy to email.
* **CLI Support:** Fully configurable via command line using [Google Fire](https://github.com/google/python-fire).

---

## 🛠️ Installation

### Prerequisites

* Python 3.8+

### 1. Clone the Repository

```shell
git clone https://github.com/SeqLaz/PyXStepRecorder.git
cd PyXStepRecorder
```

### 2. Set Up Environment

Recommended using a virtual environment:

```shell
python -m venv .venv
source venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Usage

PyXStepRecorder uses a CLI interface. You can define your output path, custom cursor, and image quality directly from your terminal.

### Quick Start

```shell
cd py_xsr
python py_xsr.py --outfile="./steps/my_guide_001.html"
```

### Advanced Configuration

| Flag      | Short | Default               | Description                                          |
|-----------|-------|-----------------------|------------------------------------------------------|
| --outfile | -o    | recording.html        | Path and name of the final HTML file.                |
| --cursor  | -c    | resources/Cursor.png  | Path to the PNG image used for the click overlay.    |
| --png     | -p    | True                  | Use PNG for lossless quality. Set to False for JPEG. |
| --quality | -q    | 80                    | Image compression quality (1-100).                   |

Using flags for custom settings:

```shell
python ./py_xsr/py_xsr.py --outfile="./docs/tutorial_01.html" --cursor="./assets/custom_pointer.png" --quality=60 --png=False
```

Upon stopping the script (usually Ctrl+C), it wraps all captured steps into a responsive HTML template.

## 📄 License

Distributed under the MIT License. See LICENSE for more information.
