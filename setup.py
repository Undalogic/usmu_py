import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="usmu_py",
    version="1.0.0",
    author="Joel Troughton",
    author_email="joel.troughton@undalogic.com",
    description="A simple Python library for controlling the uSMU source-measure unit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Undalogic/usmu_py",  
    packages=setuptools.find_packages(),  
    install_requires=[
        "pyserial>=3.0",
        "numpy>=1.18",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
