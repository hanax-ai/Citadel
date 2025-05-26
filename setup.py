
"""
Setup script for Project Citadel.
"""

from setuptools import setup, find_packages

setup(
    name="citadel_revisions",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "beautifulsoup4",
        "requests",
        "PyPDF2",
        "langchain",
        "langchain-core",
        "langchain-text-splitters",
        "faiss-cpu",
        "numpy",
        "langgraph>=0.0.15",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "isort",
        ],
        "ocr": [
            "pytesseract",
            "Pillow",
        ],
    },
)
