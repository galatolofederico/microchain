import setuptools
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="microchain-python",
    version="0.3.7",
    author="Federico A. Galatolo",
    author_email="federico.galatolo@unipi.it",
    description="",
    url="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["microchain", "microchain.models", "microchain.engine"],
    install_requires=[
        "termcolor==2.4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ],
)