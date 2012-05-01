import os

# Downloads setuptools if not find it before try to import
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

packages = ['articles']

setup(
    name='London articles',
    version=0.1,
    #url='',
    author="Bruno Gola",
    license="BSD License",
    packages=packages,
    )

