import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BeauCoup",  
    version="0.0",
    author="Nick Richardson and Dmitry Paramonov",
    author_email="njkrichardson@princeton.edu",
    description="BeauCoup implementation and Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/njkrichardson/BeauCoup",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Jinja2 == 2.11.2",
    ]
)