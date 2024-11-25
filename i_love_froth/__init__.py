"""The main module for Bubble Analyser."""
from .image_analysis import VideoAnalysis
from .arrow import Arrow
from .autosaver import AutoSaver
from .gui import MainGUI
from .video_recorder import VideoRecorder
from .roi import ROI
from .export import Export
from importlib.metadata import version

__version__ = version(__name__)
