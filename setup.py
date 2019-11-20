import platform
from distutils.core import setup

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

setup(
        author = 'Daniel Popiniuc',
        author_email = 'danielpopiniuc@gmail.com',
        dependency_links = [
            url__tableau_hyper_api
        ],
        description = 'Wrapper to ease data management into Tableau Hyper format',
        license = 'LGPL3',
        long_description = long_description_readme,
        long_description_content_type = "text/markdown",
        name = 'tableau-hyper-management',
        python_requires = '>=3.6',
        version = '1.0',
        download_url = '',
)
