from distutils.core import setup

setup(
    name='tableauhypermanagement',
    version='1.0',
    author='Daniel Popiniuc',
    description='Wrapper to ease data management into Tableau Hyper format',
    packages=['tableauhyperapi'],
    requires=['tableauhyperapi'],
    python_requires='>=3.6',
)
