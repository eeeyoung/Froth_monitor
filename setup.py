from setuptools import setup, find_packages

setup(
    name="i_love_froth",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "i_love_froth = i_love_froth.__main__:main",
        ],
    },
)