try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


with open('jsvnews/venv/requirements.txt') as F:
    deps = [n for n in F.read().split('\n') if ' ' not in n]
setup(name='jsvnews',
      version='0.1.0',
      author='Julian Vanecek',
      author_email='julian.vanecek@gmail.com',
      packages=find_packages(),
      install_requires=deps,
      url='www.github.com/jsvan',
      )