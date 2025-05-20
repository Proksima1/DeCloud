from setuptools import find_packages, setup

setup(
    name="decloud",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "pydantic-settings",
        "python-multipart",
        "aiohttp",
    ],
)
