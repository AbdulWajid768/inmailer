from setuptools import setup, find_packages

setup(
    name="py_mailer",
    version="0.1.0",
    author="Abdul Wajid",
    author_email="abdul45.wajid@gmail.com",
    description="A Python package that offers email utilities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AbdulWajid768/pymailer",
    packages=find_packages(),
    install_requires=[
        "cssutils",
        "lxml",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6, <=3.13",
)
