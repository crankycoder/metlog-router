from setuptools import setup, find_packages
import sys, os

version = '0.1'

requires = ['docopt', 'gevent']

setup(name='metlog-router',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[],
      keywords='metlog router',
      author='Rob Miller',
      author_email='rmiller@mozilla.com',
      url='',
      license='MPLv2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
