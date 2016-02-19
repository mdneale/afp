# afp module's setup.py
from distutils.core import setup
setup(
    name='afp',
    version='0.1',
    author='Matthew Neale',
    author_email='matt@matthewneale.net',
    url='https://github.com/mdneale/afp',
    description='Python package and utilities for reading AFP (Advanced Function Presentation) files',
    py_modules=['afp2ascii', 'dumpafp'],
    packages=['afp'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Printing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    long_description = """\
afp
---

Python package and utilities for reading AFP (Advanced Function Presentation)
files.

Overview
--------

An afp package for Python, allowing the caller to read and decode AFP (Advanced
Function Presentation) print files. For more information on AFP see the website
of the AFP Consortium http://afpcinc.org.

The repository also contains two utilities that make use of the library -
dumpafp.py and afp2ascii.py.

The code is pure Python 3.
"""
)
