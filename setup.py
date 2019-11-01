import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="duplremover",
    version="0.0.2",
    author="GuardianAngel",
    author_email="zhling2012@live.com",
    description="remove any duplicated files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GuardianGH/duplremover/tree/master/duplremover",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[]
)