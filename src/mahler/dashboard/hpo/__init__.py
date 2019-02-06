# -*- coding: utf-8 -*-
"""
:mod:`mahler.dashboard.hpo -- Dashboard to visualization HPO with ASHA
=======================================================================

.. module:: hpo
    :platform: Unix
    :synopsis: TODO

TODO: Write long description
"""
from ._version import get_versions
from .main import main

VERSIONS = get_versions()
del get_versions

__descr__ = 'Dashboard to visualization HPO with ASHA'
__version__ = VERSIONS['version']
__license__ = 'GNU GPLv3'
__author__ = u'Xavier Bouthillier'
__author_short__ = u'Xavier Bouthillier'
__author_email__ = 'xavier.bouthillier@umontreal.ca'
__copyright__ = u'2019, Xavier Bouthillier'
__url__ = 'https://github.com/bouthilx/mahler.dashboard.hpo'


def build_parser(parser):
    """Return the parser that needs to be used for this command"""
    hpo_parser = parser.add_parser('hpo', help='local help')

    # Add arguments...
    # hpo_parser.add_argument(
    #     '--processes', type=int, default=CPU_COUNT,
    #     help='number of concurrent process to spawn. Default: number of CPUs available')

    # Set main function to execute
    hpo_parser.set_defaults(func=main)
