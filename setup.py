from __future__ import print_function
from setuptools import setup

import terse

#long_description = read('README.txt')
long_description = ''

setup(
    name='terse',
#    version=terse.__version__,
    version=0.8,
    url='https://github.com/ComputationalChemistry-NMSU/terse',
    license='MIT Software License',
    author='Marat Talipov',
    install_requires=['logging',
                    'argparse',
                    ],
    author_email='talipovm@nmsu.edu',
    description='High-throughput analyzer/visualizer of quantum chemistry calculations',
    long_description=long_description,
    packages=['terse'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 2 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        ],
)
