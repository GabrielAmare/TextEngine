import setuptools
import pkg_resources
import sys
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = list(map(str, pkg_resources.parse_requirements(fh.read())))

sys.argv.append("sdist")
sys.argv.append("bdist_wheel")

python_dir = os.path.dirname(sys.executable) + "\\python.exe"
pckg_dir = os.path.abspath(os.curdir)

setuptools.setup(
    name="TextEngine",
    version="1.0.1",
    author="Gabriel Amare",
    author_email="gabriel.amare.31@gmail.com",
    description="Easy implementation of lexical & syntax analysis for formal language analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/GabrielAmare/TextEngine",
    packages=['text_engine', 'text_engine.base', 'text_engine.core'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

if input("Build successful, upload to testpypi ? (Y/n)") == "Y":
    os.system(python_dir + ' -m twine upload --repository testpypi dist/*')
