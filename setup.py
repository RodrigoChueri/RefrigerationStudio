

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("angulo_solar2.pyx")
)



