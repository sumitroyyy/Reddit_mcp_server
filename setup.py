from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="reddit-mcp-server",
    version="1.0.0",
    author="Sumit Roy",
    author_email="devopsroyy@gmail.com",
    description="A comprehensive MCP server for Reddit API access",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sumitroyyy/reddit-mcp-server",
    packages=find_packages(),
    py_modules=["server"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "reddit-mcp-server=server:main",
        ],
    },
    keywords="mcp, reddit, api, claude, ai, assistant, model-context-protocol",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/reddit-mcp-server/issues",
        "Source": "https://github.com/yourusername/reddit-mcp-server",
        "Documentation": "https://github.com/yourusername/reddit-mcp-server#readme",
        "MCP Directory": "https://mcpservers.org",
    },
)