from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="hotel_reservation",
    version="0.1",
    author="Bharath",
    author_email="bharath.vasanthkumar@gmail.com",
    description="A hotel reservation system",
    packages=find_packages(),
    install_requires=requirements,
)
