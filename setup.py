"""
setup - ensures proper package setup

This file is ensuring proper package setup is performed to ensure all prerequisites are satisfied 
and correct execution is possible
"""
# standard Python packages
import platform
from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description_readme = fh.read()

this_package_website = 'https://github.com/danielgp/tableau-hyper-management'
tableau_hyper_website_download = 'http://downloads.tableau.com/tssoftware/tableauhyperapi-'
tableau_hyper_api__current_known_version = '0.0.9746'  # released on 2020-01-29
url__tableau_hyper_api = tableau_hyper_website_download + tableau_hyper_api__current_known_version

if platform.system() == 'Windows':
    url__tableau_hyper_api += '-py3-none-win_amd64.whl'
elif platform.system() == 'Darwin':
    url__tableau_hyper_api += '-py3-none-macosx_10_11_x86_64.whl'
elif platform.system() == 'Linux':
    url__tableau_hyper_api += '-py3-none-linux_x86_64.whl'
else:
    url__tableau_hyper_api += '-py3-none-linux_x86_64.whl'

setup(
    author = 'Daniel Popiniuc',
    author_email = 'danielpopiniuc@gmail.com',
    classifiers = [
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
    dependency_links = [
        url__tableau_hyper_api
    ],
    description = 'Wrapper to ease data management into Tableau Hyper format from CSV files',
    include_package_data = True,
    install_requires = [
        'cffi>=1.13.2,<2',
        'numpy>=1.17.4,<=1.18.1',
        'pandas>=0.25.3,<=1.0.1',
        'tableauhyperapi>=0.0.8707,<=0.0.9746'
    ],
    keywords = [
        'tableau',
        'hyper',
        'csv'
    ],
    license = 'LGPL3',
    long_description = long_description_readme,
    long_description_content_type = 'text/markdown',
    name = 'tableau-hyper-management',
    package_data = {
        '': [
            '*.json',
            '*.md'
        ]
    },
    packages = find_packages(),
    project_urls = {
        'Documentation': this_package_website + '/blob/master/README.md',
        'Issue Tracker': this_package_website + '/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc',
        'Source Code': this_package_website
    },
    python_requires = '>=3.6',
    url = this_package_website + '/releases',  # project home page, if any
    version = '1.2.3'
)
