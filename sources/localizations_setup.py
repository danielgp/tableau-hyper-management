"""
localization_setup - facilitates localization activities
"""
# facilitate dependencies management
from setuptools import setup
# facilitate internationalization
from babel.messages import frontend

setup(
    cmdclass={
        'compile_catalog': frontend.compile_catalog,
        'update_catalog': frontend.update_catalog
    }
)
