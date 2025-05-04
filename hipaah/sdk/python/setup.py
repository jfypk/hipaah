from setuptools import setup, find_packages

setup(
    name="hipaah",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "typer>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "hipaah=hipaah.cli.cli:app",
        ],
    },
)