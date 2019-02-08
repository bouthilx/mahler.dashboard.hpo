import datetime
import multiprocessing
import random
import time

import json

import dash
import dash_html_components as html

from flask_caching import Cache


from . import layout
from . import callback
from . import observer



external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def build(options):
    cache, redis_client = build_cache(app, {})

    callbacks_component = callback.build(redis_client, dataset_names=options['dataset_names'],
                                         model_names=options['model_names'])

    layout_component = layout.build(redis_client, dataset_names=options['dataset_names'],
                                    model_names=options['model_names'])
    
    app.layout = html.Div([layout_component, callbacks_component])

    callback.register(app, redis_client, options['dataset_names'], options['model_names'])

    observers = observer.build(redis_client, options['dataset_names'], options['model_names'])
 
    p = multiprocessing.Process(target=query, args=(observers, {}), daemon=True)
    p.start()

    # query(observers, {})

    # TODO: build daemons for each plotter computations, no signal is fired when
    #       new computations ready.

    return app


def __dummy_query():
    trials = []
    for dataset_name in ['mnist', 'svhn', 'cifar10']:
        for model_name in ['lenet', 'vgg11', 'resnet18']:
            for algo_name in ['random-search', 'ASHA', 'BO', 'evo']:
                all_stats = [dict(epoch=0)]
                for set_name in 'train valid test'.split(" "):
                    all_stats[0][set_name] = dict(
                        loss=random.random(),
                        error_rate=100)
                best_stats = all_stats[0]

                for i in range(100):
                    # To have different lengths
                    if random.random() > 0.95:
                        break

                    stats = dict(epoch=all_stats[-1]['epoch'] + 1)
                    for set_name in 'train valid test'.split(" "):
                        stats[set_name] = dict(
                            loss=all_stats[-1][set_name]['loss'] - random.random(),
                            error_rate=all_stats[-1][set_name]['error_rate'] - random.random())

                    if stats['valid']['error_rate'] < best_stats['valid']['error_rate']:
                        best_stats = stats

                    all_stats.append(stats)

                output = dict(all_stats=all_stats, best_stats=best_stats)

                trial = dict(
                    id=str(int(random.random() * 1000)),
                    output=output,
                    registry=dict(
                        status='Completed' if random.random() > 0.5 else 'Running',
                        duration=len(all_stats) * 1.,
                        tags=['alpha-v1.0.0', dataset_name, model_name, algo_name,
                              'train' if random.random() > 0.05 else 'create_trial',
                              'hpo' if random.random() > 0.2 else 'distrib',
                              random.choice('min max mean'.split(' '))],
                        start_time=str(datetime.datetime.now())))

                if 'create_trial' in trial['registry']['tags']:
                    trial['output'] = {}

                trials.append(trial)

    return trials


def query(observers, options):

    # import pdb
    # pdb.set_trace()

    while True:
        # Fetch data
        # for each document, register for each observer
        for document in __dummy_query():
            for observer in observers:
                observer.register(document)
        print('sleeping')
        time.sleep(1)


class Observer:
    def __init__(self, key, client):
        self.key = key
        self.client = client

    def register(self, document):
        # Filter based on different things observer needs to monitor
        self.client.rpush(self.key, json.dumps(document))


def build_cache(app, options):
    CACHE_CONFIG = {
        'CACHE_TYPE': 'redis',
        'CACHE_KEY_PREFIX': 'fcache',
        'CACHE_REDIS_HOST': 'localhost',
        'CACHE_REDIS_PORT': '6379',
        'CACHE_REDIS_URL': 'redis://localhost:6379'
    }
    cache = Cache()
    cache.init_app(app.server, config=CACHE_CONFIG)

    redis_client = next(iter(cache.app.extensions['cache'].values()))._client

    redis_client.flushdb()

    return cache, redis_client
