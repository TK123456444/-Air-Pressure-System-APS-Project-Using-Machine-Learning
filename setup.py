from setuptools import find_packages,setup
from typing import List
def requirement_list()->list[str]:
    requirement_list: list[str] = []
    return requirement_list
    pass
setup(
    name="sensor",
    version="0.0.1",
    author="Tushar",
    author_email="tukumawat73@gmail.com",
    packages=find_packages(),
    install_requires= requirement_list()

)