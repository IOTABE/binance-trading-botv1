from setuptools import setup, find_packages

setup(
    name="binance-trading-botv1",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-socketio",
        "python-binance",
        "python-dotenv",
        "pandas",
        "numpy",
        "ta",
        "gunicorn",
        "eventlet"
    ],
    python_requires=">=3.8",
)
