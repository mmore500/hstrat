#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "anytree>=2.8.0",
    "iterpop>=0.3.4",
    "interval_search>=0.1.2",
    "gmpy>=1.17",
    "matplotlib>=3.1.2",
    "opytional>=0.1.0",
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Matthew Andres Moreno",
    author_email='m.more500@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="hstrat enables phylogenetic inference on distributed digital evolution populations",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='hstrat',
    name='hstrat',
    packages=find_packages(include=['hstrat', 'hstrat.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mmore500/hstrat',
    version='0.2.0',
    zip_safe=False,
)
