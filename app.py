import os


# Default to demo mode on Spaces; override locally with DEMO_MODE=0
os.environ.setdefault("DEMO_MODE", "1")

from src.interface import demo

demo.launch()
