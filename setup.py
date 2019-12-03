import platform
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description_readme = fh.read()

tableau_hyper_api__current_known_version = '0.0.8953'

if platform.system() == 'Windows':
    url__tableau_hyper_api = 'http://downloads.tableau.com/tssoftware/tableauhyperapi-'\
                             + tableau_hyper_api__current_known_version \
                             + '-py3-none-win_amd64.whl'
elif platform.system() == 'Darwin':
    url__tableau_hyper_api = 'http://downloads.tableau.com/tssoftware/tableauhyperapi-'\
                             + tableau_hyper_api__current_known_version \
                             + '-py3-none-macosx_10_11_x86_64.whl'
elif platform.system() == 'Linux':
    url__tableau_hyper_api = 'http://downloads.tableau.com/tssoftware/tableauhyperapi-'\
                             + tableau_hyper_api__current_known_version \
                             + '-py3-none-linux_x86_64.whl'
else:
    url__tableau_hyper_api = 'http://downloads.tableau.com/tssoftware/tableauhyperapi-'\
                             + tableau_hyper_api__current_known_version \
                             + '-py3-none-linux_x86_64.whl'

_setup(
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
    keywords = [
        'tableau',
        'hyper',
        'csv'
    ],
    license = 'LGPL3',
    license_file = 'LICENSE',
    long_description = long_description_readme,
    name = 'tableau-hyper-management',
    package_data = {
        '': ['*.json', '*.md']
    },
    packages = find_packages(),
    project_urls = {
        "Documentation": "https://github.com/danielgp/tableau-hyper-management/blob/master/README.md",
        "Issue Tracker": "https://github.com/danielgp/tableau-hyper-management/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc",
        "Source Code": "https://github.com/danielgp/tableau-hyper-management"
    },
    python_requires = '>=3.6',
    url = 'https://github.com/danielgp/tableau-hyper-management/releases', # project home page, if any
    version = '1.0.0'
)
