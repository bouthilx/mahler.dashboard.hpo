#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Installation script for `mahler.dashboard.hpo`."""
import os

from setuptools import setup

import versioneer


repo_root = os.path.dirname(os.path.abspath(__file__))

tests_require = ['pytest>=3.0.0']

setup_args = dict(
    name='mahler.dashboard.hpo',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Dashboard to visualization HPO with ASHA',
    long_description=open(os.path.join(repo_root, "README.rst")).read(),
    license='GNU GPLv3',
    author=u'Xavier Bouthillier',
    author_email='xavier.bouthillier@umontreal.ca',
    url='https://github.com/bouthilx/mahler.dashboard.hpo',
    packages=['mahler.dashboard.hpo'],
    package_dir={'': 'src'},
    include_package_data=True,
    # data_files=find_data_files(),
    entry_points={
        'Dashboard': [
            'hpo = mahler.dashboard.hpo'
            ],
        },
    install_requires=['mahler.core', 'mahler.registry.mongodb',
                      'tzlocal', 'python-dateutil',
                      'dash', 'dash_core_components', 'dash_html_components', 'dash_table',
                      # For laoding stats; from https://community.plot.ly/t/mega-dash-loading-states/5687
                      'dash_renderer',
                      # For caching
                      'redis',
                      'plotly', 'flask_caching', 'numpy'],

    tests_require=tests_require,
    setup_requires=['setuptools', 'pytest-runner>=2.0,<3dev'],
    extras_require=dict(test=tests_require),
    # "Zipped eggs don't play nicely with namespace packaging"
    # from https://github.com/pypa/sample-namespace-packages
    zip_safe=False
    )

setup_args['keywords'] = [
    ]

setup_args['platforms'] = ['Linux']

setup_args['classifiers'] = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GPU GPLv3',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
] + [('Programming Language :: Python :: %s' % x)
     for x in '3 3.5 3.6 3.7'.split()]

if __name__ == '__main__':
    setup(**setup_args)
