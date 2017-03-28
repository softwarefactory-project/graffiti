#!/usr/bin/env python
"""Setup
"""

import re
import setuptools
from graffiti import __version__


def requires():
    """Retrieve requirements from requirements.txt
    """
    try:
        reqs = map(str.strip, open('requirements.txt').readlines())
        reqs = filter(lambda s: re.match(r'\W', s), reqs)
        return reqs
    except Exception:
        pass
    return []


setuptools.setup(
    name='graffiti',
    version=__version__,
    description='RDO builds tagging utility',
    author='Haikel Guemar',
    author_email='hguemar@fedoraproject.org',
    url='https://github.com/hguemar/graffiti',
    packages=[
        'graffiti'
    ],
    install_requires=requires(),
    entry_points={
        'console_scripts': ['graffiti = graffiti.cli:main']
    }
)
