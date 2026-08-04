from setuptools import setup, find_packages
from typing import List

HYPHEN_E_DOT = "-e ."

def requirement_list() -> List[str]:
    requirements = []

    with open("requirements.txt") as file:
        requirements = file.readlines()
        requirements = [req.strip() for req in requirements]

        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)

    return requirements


setup(
    name="sensor",
    version="0.0.1",
    author="Tushar",
    author_email="tukumawat73@gmail.com",
    packages=find_packages(),
    install_requires=requirement_list(),
)

