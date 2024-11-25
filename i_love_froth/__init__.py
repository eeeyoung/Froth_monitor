"""The main module for Bubble Analyser."""
<<<<<<< HEAD
from .image_analysis import VideoAnalysisModule
=======
from .image_analysis import VideoAnalysis
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
from .arrow import Arrow
from .autosaver import AutoSaver
from .gui import MainGUI
from .video_recorder import VideoRecorder
from .roi import ROI
<<<<<<< HEAD
from .export import Export
=======
from .export import Export
from importlib.metadata import version

__version__ = version(__name__)
>>>>>>> 1109b73 (Completion of docstrings, test files and poetry dependencies file)
