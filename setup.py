from setuptools import setup, find_packages

with open("README.md", mode="r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(name='konoise', # 패키지 명

version='1.0.4.8',

description='Korean Noise Generator',
long_description=long_description,
long_description_content_type="text/markdown",
url="https://github.com/wisenut-research/konoise",

author='Eddie',

author_email='hkjeo13@gmail.com',

license='MIT',

py_modules=['konoise'],

python_requires='>=3',

install_requires=[],

packages=['konoise']

install_requires=['tqdm'],

)