#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


from setuptools import find_packages, setup
import os

URL = 'https://github.com/TMAN-Lab/tman-atlassian-atc-manager'

NAME = 'atlassian-auto-test-case-manager'

if os.getenv("BITBUCKET_TAG"):
    VERSION = os.getenv("BITBUCKET_TAG").lower().replace("v", "")
else:
    ver_dev_file = "version_dev.txt"
    if not os.path.exists(ver_dev_file):
        with open(ver_dev_file, "w", encoding="utf-8") as f:
            f.write("0.1")
    with open(ver_dev_file, 'r', encoding="utf-8") as f:
        version = f.read().strip()
    ver_major, ver_minor = version.split(".")
    ver_next = int(ver_minor) + 1
    VERSION = ".".join([str(ver_major), str(ver_next)])
    with open(ver_dev_file, 'w') as f:
        f.write(VERSION)

DESCRIPTION = 'Extract test cases from your codebase and push them into Jira with a single command.'

if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = DESCRIPTION

AUTHOR = 'Will'
AUTHOR_EMAIL = 'will.shi@tman.ltd'

LICENSE = 'Apache'

PLATFORMS = [
    'linux',
]

REQUIRES = [
    'PyYAML',
    'tabulate',
    'requests',
]

CONSOLE_SCRIPTS = 'atlas-atc-manager=atlassian_atc_manager.main:main'

PKG_DATA = {}

setup(
    name=NAME,
    version=VERSION,
    description=(
        DESCRIPTION
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    package_data=PKG_DATA,
    platforms=PLATFORMS,
    url=URL,
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [CONSOLE_SCRIPTS],
    }
)
