from distutils.core import setup
from setuptools import find_packages

setup(name='moveax-sdk-boilerplate',
      version='1.1.1',
      packages=find_packages(),
      install_requires=['requests>=2.20.0,<3', 'moveax-validation==1.1.2'],
      description='A simple SDK boilerplate',
      author='MovEax',
      author_email='simone.bronzini@moveax.it',
      url='https://github.com/moveaxlab/sdk-boilerplate-py',
      python_requires='>=3',
      keywords=['sdk', 'api', 'validation', 'boilerplate'])
