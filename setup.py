"""Compatibility setup.py for editable installs on older build frontends."""

from setuptools import find_packages, setup


setup(
    name="cost-agent-mot",
    version="0.1.0",
    description="Cost-aware detector-tracker scheduling for remote-sensing multi-object tracking.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Anonymous Authors",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={"console_scripts": ["cost-agent-mot=cost_agent_mot.cli:main"]},
)
