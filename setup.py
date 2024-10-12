from setuptools import setup

setup(
    name="pygui",
    version="0.1",
    py_modules=["pygui"],
    packages=[],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    description="A framework for building GUIs on top of pygame.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    install_requires=[],
    python_requires=">=3.8",
    test_suite="",
    url="https://github.com/rj79/pygui",
    author="Robert Johansson",
    author_email="robertrockar@live.com",
)
