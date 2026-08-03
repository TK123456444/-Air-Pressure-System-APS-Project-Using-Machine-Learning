from setuptools import setup, find_packages
from typing import List


def requirement_list() -> List[str]:
    requirements: List[str] = []

    with open("requirements.txt", "r") as file:
        requirements = [
            line.strip()
            for line in file
            if line.strip() and not line.startswith("#")
        ]

    return requirements


setup(
    name="sensor",
    version="0.0.1",
    author="Tushar",
    author_email="tukumawat73@gmail.com",
    packages=find_packages(),
    install_requires=requirement_list(),
)