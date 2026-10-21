import os

# Must be set before pytest-qt creates the QApplication so tests run without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
