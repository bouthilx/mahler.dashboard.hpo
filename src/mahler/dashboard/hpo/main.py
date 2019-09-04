# -*- coding: utf-8 -*-
"""
:mod:`mahler.dashboard.hpo.main -- Main function of the dashboard cli 
=====================================================================

.. module:: hpo
    :platform: Unix
    :synopsis: TODO

TODO: Write long description
"""
from mahler.dashboard.hpo import app

from mahler.dashboard.hpo import config


def main(options):
    run_options = dict(debug=False, port=5011, host='0.0.0.0', threaded=True, processes=1)
    options = dict(dataset_names=config.dataset_names,
                   model_names=config.model_names)
    app.build(options).run_server(**run_options)
