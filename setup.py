#!/usr/bin/python

from setuptools import setup, find_packages

version = '0.0.1'

setup(name='bringyourownproxies',
      version=version,
      description="bring your own proxies system",
      long_description="",
      # Strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='MIT',
      packages=['bringyourownproxies'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite='nose.collector'
      )