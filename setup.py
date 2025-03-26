from setuptools import setup, find_packages

setup(
    name="froth_monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "froth_monitor = froth_monitor.__main__:main",
        ],
    },
)