"""
localization_setup - facilitates localization activities
"""
# facilitate internationalization
from babel.messages import frontend

setup(
    cmdclass={
        'compile_catalog': frontend.compile_catalog,
        'init_catalog': frontend.init_catalog,
        'update_catalog': frontend.update_catalog
    }
)
