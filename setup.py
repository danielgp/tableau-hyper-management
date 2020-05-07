"""
setup - ensures proper package setup

This file is ensuring proper package setup is performed to ensure all prerequisites are satisfied 
and correct execution is possible
"""
# package to handle files/folders and related metadata/operations
import os
# package to facilitate multiple operation system operations
import platform
# facilitate dependencies management
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as fh:
    long_description_readme = fh.read()

this_package_website = 'https://github.com/danielgp/tableau-hyper-management'

setup(
    author='Daniel Popiniuc',
    author_email='danielpopiniuc@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    description='Wrapper to ease data management into Tableau Hyper format from CSV files',
    include_package_data=True,
    install_requires=[
        'Babel>=2.8.0,<3',
        'cffi>=1.13.2,<2',
        'codetiming>=1.1,<2',
        'numpy>=1.17.4,<2',
        'pandas>=0.25.3,<1',
        'tableauhyperapi',
        'tableauserverclient',
        'xlrd>=1,<2',
        'xlsxwriter>=1,<2'
    ],
    keywords=[
        'tableau',
        'hyper',
        'csv',
        'json',
        'excel',
        'pickle'
    ],
    license='LGPL3',
    long_description=long_description_readme,
    long_description_content_type='text/markdown',
    name='tableau-hyper-management',
    packages=find_packages('tableau_hyper_management'),
    package_data={
        'samples': [
            '*.json'
        ],
        'tableau_hyper_management': [
            '*.json'
        ]
    },
    project_urls={
        'Documentation': this_package_website + '/blob/master/README.md',
        'Issue Tracker': this_package_website +
                         '/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc',
        'Source Code': this_package_website
    },
    python_requires='>=3.6',
    url=this_package_website + '/releases',  # project home page, if any
    version='1.3.10'
)
