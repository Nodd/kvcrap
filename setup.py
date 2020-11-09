import setuptools

with open("README.rst", "rt", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crapette",
    version="0.0.1",
    author="Joseph Martinot-Lagarde",
    author_email="contrebasse+pypi@gmail.com",
    description="A crapette card playing game, made with kivy and love.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/Nodd/kvcrap.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Kivy",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    python_requires=">=3.6",
    install_requires=["kivy"],
)
