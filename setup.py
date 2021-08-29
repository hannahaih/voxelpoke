from setuptools import setup
from Cython.Build import cythonize
from distutils.core import Extension, setup

setup(
    name='city_builder',
    version='1.0',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    ext_modules=cythonize(Extension(name="voxels_to_mesh", sources=["voxels_to_mesh.pyx"]), compiler_directives={'language_level' : "3"})
)
