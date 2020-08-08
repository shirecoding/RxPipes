from distutils.core import setup
from setuptools import find_packages
from rxpipes import __version__

setup(
    name='rxpipes',
    version=__version__,
    author='shirecoding',
    install_requires=[
        'rx'
    ],
    url='https://github.com/shirecoding/RxPipes',
    long_description=open('README.md').read(),
    zip_safe=False,
    include_package_data=True,
    packages=find_packages() + [],
    package_data={}
)