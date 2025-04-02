from setuptools import setup, find_packages

setup(
    name="app-review-monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "appstoreconnect>=0.13.0",
        "slack-sdk>=3.27.1",
        "python-dotenv>=1.0.0",
        "schedule>=1.2.1",
        "pytz>=2024.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-mock>=3.12.0",
            "python-json-logger>=2.0.7",
            "pre-commit>=3.6.0",
            "black>=24.1.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "flake8-docstrings>=1.7.0",
            "mypy>=1.8.0",
            "tox>=4.15.0",
        ],
    },
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "app-review-monitor=app_review_monitor.cli:main",
        ],
    },
) 