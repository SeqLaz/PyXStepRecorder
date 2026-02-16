"""
PyXStepRecorder: A Python utility for recording screen interactions.

This script listens for mouse clicks globally, captures a screenshot at each
click with a custom cursor overlay, and compiles the sequence of steps into
an HTML report. It relies on `pynput` for input monitoring and `Pillow` for
image processing.

Usage:
    Can be run as a standalone CLI tool via `fire`.
    Example: python script_name.py --outfile="report.html" --png=True
"""

import sys
import time
import tempfile
import shutil
from threading import Lock, Event
from dataclasses import dataclass, field
from typing import List, Optional, Any
from pathlib import Path

from html_exporter import GenerateReport

try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button
    from PIL import Image, ImageGrab
except ImportError:
    print("Missing dependencies. Run:\n")
    print("pip install pynput Pillow")
    sys.exit(1)


@dataclass
class RecorderConfig:
    """
    Configuration settings for the screen recorder.

    Attributes:
        outfile (Path): The absolute path where the final HTML report will be saved.
            Defaults to current path with the name in "steps/Steps_Recorded.html".
        cursor_path (Path): Path to the custom cursor image file.
            Defaults to current path in "resources/Cursor.png".
        image_ext (str): The image extension/format to use (e.g., "png", "jpg").
            Defaults to "png".
        quality (int): The compression quality for the saved images (1-100).
            Defaults to 80.
    """

    outfile: Path = field(default_factory=lambda: Path("steps/Steps_Recorded.html"))
    cursor_path: Path = field(default_factory=lambda: Path("resources/Cursor.png"))
    image_ext: str = "png"
    quality: int = 80

    @property
    def title(self) -> str:
        """Returns the title of the recording based on the output filename stem."""
        return Path(self.outfile).stem


@dataclass
class RecordedStep:
    """
    Represents a single recorded action in the timeline.

    Attributes:
        description (str): Text description of the action (e.g., "Left-click").
        image_filename (Optional[str]): The filename of the screenshot associated
            with this step. Defaults to None.
        timestamp (float): The Unix timestamp when the step occurred.
            Defaults to the current time.
    """

    description: str
    image_filename: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class PyXStepRecorder:
    """
    Main controller for recording screen interactions and generating screenshots.

    It handles the mouse listener, screenshot capture, thread safety,
    and HTML generation.

    Attributes:
        cfg (RecorderConfig): The configuration object for this session.
        lock (Lock): Threading lock to ensure screenshots and list appends
            don't overlap.
        is_recording (bool): Flag indicating if the recording loop is active.
        steps (List[RecordedStep]): A chronological list of recorded actions.
        _temp_dir (Path): Temporary directory for storing screenshots before
            HTML generation.
        _screen_counter (int): Counter to ensure unique screenshot filenames.
        __stop_event (Event): Caller for the stop event.
    """

    cfg: RecorderConfig
    lock: Lock = field(default_factory=Lock)
    is_recording: bool = True
    steps: List[RecordedStep] = field(default_factory=list)
    _temp_dir: Path = field(default_factory=lambda: Path(tempfile.mkdtemp()))
    _screen_counter: int = 0
    _stop_event: Event = field(default_factory=Event)

    def __post_init__(self) -> None:
        """Initializes the mouse controller and loads the cursor image."""
        self.mouse_controller: mouse.Controller = mouse.Controller()
        self.cursor_img: Optional[Image.Image] = self._load_cursor()

    def _load_cursor(self) -> Image.Image | None:
        """
        Loads the custom cursor image from the configuration path.

        Returns:
            Image.Image | None: The RGBA converted Pillow Image object if found,
            otherwise None.
        """
        if self.cfg.cursor_path and Path(self.cfg.cursor_path).exists():
            try:
                return Image.open(self.cfg.cursor_path).convert("RGBA")
            except Exception as e:
                print("Error loading the cursor image provided")
                print(f"\n{e}")
        return None

    def _take_screenshot(self) -> Optional[str]:
        """
        Captures the screen, overlays the cursor, and saves to a temp file.

        Returns:
            Optional[str]: The filename of the saved screenshot, or None if
            an error occurred.
        """
        try:
            screenshot = ImageGrab.grab()
            mouse_x, mouse_y = self.mouse_controller.position
            final_image = screenshot.copy()

            if self.cursor_img is not None:
                final_image.paste(
                    self.cursor_img, (int(mouse_x), int(mouse_y)), self.cursor_img
                )

            filename = (
                f"{self.cfg.title}_step_{self._screen_counter}.{self.cfg.image_ext}"
            )
            path = Path(self._temp_dir) / filename

            save_args: dict[str, Any] = {}
            if self.cfg.image_ext.lower() in ["jpg", "jpeg"]:
                save_args["quality"] = self.cfg.quality

            final_image.save(path, **save_args)

            self._screen_counter += 1
            return filename

        except Exception as e:
            print(f"Screenshot error: {e}")
            print("Please stop, and review the path to the cursor is correct!")
            return None

    def _add_step(self, description: str) -> None:
        """
        Thread-safe method to capture a screenshot and record a step.

        Args:
            description (str): The description of the user action (mouse clicks).
        """
        with self.lock:
            if not self.is_recording:
                return
            img_file = self._take_screenshot()
            step = RecordedStep(description=description, image_filename=img_file)
            self.steps.append(step)

    def _generate_html(self) -> None:
        """
        This instantiates the `GenerateReport` class, passes the temporary
        screenshots and step data, and triggers the build process.
        """

        generator = GenerateReport(
            title=self.cfg.title,
            outfile=self.cfg.outfile,
            steps=self.steps,
            temp_dir=self._temp_dir,
            image_ext=self.cfg.image_ext,
        )
        generator.generate_report()

    def on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        """
        Callback for mouse click events.

        Args:
            x (int): The x-coordinate of the mouse event.
            y (int): The y-coordinate of the mouse event.
            button: The button object (Button.left, Button.right, etc.).
            pressed (bool): True if the button was pressed, False if released.
        """
        if not pressed:
            return

        btn_map = {
            "Button.left": "Left-click",
            "Button.right": "Right-click",
            "Button.middle": "Middle-click",
        }
        button_name = str(button)
        desc = btn_map.get(button_name, f"Clicked {button_name}")
        self._add_step(desc)

    def _trigger_stop(self):
        """Callback for global hotkeys to signal the script to stop."""
        self._stop_event.set()

    def start(self) -> None:
        """Starts the mouse and keyboard listeners and the recording loop."""
        self.cfg.outfile.parent.mkdir(parents=True, exist_ok=True)

        print(f"Recording to {self.cfg.outfile}")
        print("Press Ctrl+Esc or Cmd+Esc ANYWHERE to stop capturing.")

        hotkeys = keyboard.GlobalHotKeys(
            {
                "<ctrl>+<esc>": self._trigger_stop,
                "<cmd>+<esc>": self._trigger_stop,
            }
        )

        m_listener = mouse.Listener(on_click=self.on_click)

        hotkeys.start()
        m_listener.start()

        try:
            self._stop_event.wait()
        except KeyboardInterrupt:
            # If the user happens to hit Ctrl+C inside the terminal itself
            pass
        finally:
            print("\nStopping... Please wait while the report is generated.")
            hotkeys.stop()
            m_listener.stop()
            self.stop()

    def stop(self) -> None:
        """
        Stops the recording, generates the HTML report, and cleans up temp files.
        """
        if not self.is_recording:
            return
        self.is_recording = False
        self._generate_html()
        try:
            shutil.rmtree(self._temp_dir)
        except OSError:
            pass


if __name__ == "__main__":
    import fire

    def run_recorder(
        outfile="steps/Steps_Recorded.html",
        cursor="resources/Cursor.png",
        png=False,
        quality=80,
    ):
        """
        Entry point to start the screen recorder via CLI.

        Args:
            outfile (str): Path where the generated HTML report will be saved.
                Defaults to "steps/Steps_Recorded.html".
            cursor (str): Path to the custom cursor PNG image.
                Defaults to "resources/Cursor.png".
            png (bool): If True, saves screenshots as lossless PNGs. If False,
                uses JPEG format. Defaults to False.
            quality (int): Compression quality (1-100) if saving as JPEG.
                Defaults to 80.
        """
        ext = "png" if png else "jpg"

        config = RecorderConfig(
            outfile=Path(outfile),
            cursor_path=Path(cursor),
            image_ext=ext,
            quality=quality,
        )

        recorder = PyXStepRecorder(cfg=config)
        recorder.start()

    fire.Fire(run_recorder)
