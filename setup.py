"""
Setup for pygount.
"""
import os
from setuptools import setup, find_packages

from pygount import __version__


# Read the long description from the README file.
_setup_folder = os.path.dirname(__file__)
with open(os.path.join(_setup_folder, 'README.rst'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(
    name='pygount',
    version=__version__,
    description='A sample Python project',
    long_description=long_description,
    url='https://github.com/roskakori/pygount',
    author='Thomas Aglassinger',
    author_email='roskakori@users.sourceforge.net',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='code analysis count',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'chardet>=2.0',
        'pygments>=2.0',
    ],
    entry_points={
        'console_scripts': [
            'pygount=pygount.command:main',
        ],
    },
)