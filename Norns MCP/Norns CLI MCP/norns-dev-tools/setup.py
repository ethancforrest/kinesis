#!/usr/bin/env python3
"""
Setup script for Norns development tools.
"""

from setuptools import setup, find_packages

setup(
    name="norns-dev-tools",
    version="0.1.0",
    description="Development tools for Norns",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "asyncssh>=2.13.0",
        "typer>=0.9.0",
        "rich>=13.3.5",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.9.0",
        "markdown>=3.3.0",
    ],
    entry_points={
        'console_scripts': [
            'norns=norns_cli.cli:app',
            'norns-ssh=norns_cli.norns_ssh:main',
            'norns-github=norns_cli.github_integration:main',
        ],
    },
    python_requires=">=3.7",
)