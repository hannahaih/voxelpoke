from setuptools import setup
from Cython.Build import cythonize


setup(
    name='city_builder',
    version='1.0',
    author='Petter Amland',
    author_email='pokepetter@gmail.com',
    license='MIT',
    ext_modules = cythonize("voxels_to_mesh.pyx"),
)
