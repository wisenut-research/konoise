from setuptools import setup, find_packages

setup(name='konoise', # 패키지 명

version='1.0',

description='testPackage Package',

author='Eddie',

author_email='hkjeo13@gmail.com',

license='MIT',

py_modules=['testPackage'],

python_requires='>=3',

install_requires=[], # 패키지 사용을 위해 필요한 추가 설치 패키지

packages=['testPackage'] # 패키지가 들어있는 폴더들

)