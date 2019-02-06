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


def main(options):
    run_options = dict(debug=False, port=5011, host='0.0.0.0', threaded=True, processes=1)
    options = dict(dataset_names=['mnist', 'svhn', 'cifar10'],
                   model_names=['lenet', 'vgg11', 'resnet18'])
    app.build(options).run_server(**run_options)
