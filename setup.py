from setuptools import setup, find_packages
from setuptools_rust import Binding, RustExtension

with open("README.md", mode="r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name='konoise',
    version='1.0.5.6',
    rust_extensions=[RustExtension("konoise/rust_generator", binding=Binding.PyO3)],
    description='Korean Noise Generator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wisenut-research/konoise",
    author="Eddie",
    author_email="hkjeo13@gmail.com",
    zip_safe=False,

    license="MIT",

    py_modules=["konoise"],

    python_requires=">=3",

    install_requires=["tqdm"],

    packages=["konoise"],

    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
