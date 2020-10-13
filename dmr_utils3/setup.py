#!/usr/bin/env python

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as file:
        return file.read()

setup(name='dmr_utils3',
      version='0.1.26',
      description='ETSI DMR (Digital Mobile Radio) Tier II Utilities',
      long_description='Modules to disassemble and assemble DMR packets, including generating and decoding various FEC routines',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3.5',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Communications :: Ham Radio',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
      keywords='dmr radio digital fec ecc mmdvm ham amateur radio',
      author='Cortney T. Buffington, N0MJS',
      author_email='n0mjs@me.com',
      install_requires=['bitstring>=3.1.5','bitarray>=0.8.3'],
      license='GPLv3',
      url='https://github.com/n0mjs710/dmr_utils',
      packages=find_packages()
     )
