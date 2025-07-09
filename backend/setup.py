from setuptools import setup, find_packages

setup(
    name="auraclass-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.22.0",
    ],
    python_requires=">=3.10",
) 