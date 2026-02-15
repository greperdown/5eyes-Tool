from setuptools import setup, find_namespace_packages

setup(
    name="5eyes-tool",
    version="3.2.0",
    description="Secret Intelligence Tool - Professional CLI toolkit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/YOURUSERNAME/5eyes-tool",
    py_modules=["5eyes"],  # Matches 5eyes.py filename
    entry_points={
        "console_scripts": [
            "5eyes=5eyes:main",  # Creates '5eyes' command
        ],
    },
    install_requires=[
        "pycryptodome>=3.20.0",
        "requests>=2.31.0", 
        "qrcode[pil]>=7.4.2",
        "pyperclip>=1.8.2",
        "keyring>=24.3.0",
        "colorama>=0.4.6",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
