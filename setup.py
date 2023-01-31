# -*- coding: utf-8 -*-
import os, glob, shutil
from setuptools import setup
from pyebuilder import __author__, __mail__, __version__

__dirname = os.path.dirname(os.path.realpath(__file__))
lib_name = "pyebuilder"

with open(os.path.join(__dirname, "requirements.txt"), "r", encoding = "utf-8") as reqr:
    requires = reqr.read().strip().split("\n")

with open(os.path.join(__dirname, "README.md"), "r") as rmr:
    readme = rmr.read()

for cache_dir in glob.glob(os.path.join(__dirname, lib_name, "**", "__pycache__"), recursive = True):
    shutil.rmtree(cache_dir)


setup(
    # base infos
    author = __author__, author_email = __mail__, version = __version__,
    name = lib_name,
    url = f"https://github.com/eseunghwan/{lib_name}",
    # pip infos
    python_requires = ">=3.9",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Environment :: Web Environment",
    ],
    license = "MIT",
    long_description = readme,
    long_description_content_type = "text/markdown",
    keywords = [ "python", "build", "builder", "electron-builder" ],
    # package infos
    install_requires = requires,
    setup_requires = requires,
    packages = [
        dir_path.replace(__dirname + os.path.sep, "")
        for dir_path in filter(lambda i: os.path.isdir(i) and not os.path.basename(i) == "__pycache__", glob.glob(os.path.join(__dirname, lib_name, "**"), recursive = True))
    ],
    package_data = {
        "": [
            "**/*.*",
            "**/**/*.*"
        ]
    },
    entry_points={
        "console_scripts": [
            "pyebuilder=pyebuilder.cli:main",
        ],
    },
    zip_safe = False
)
