from collections import defaultdict
import random

import json

import redis

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from . import config
from . import processor
from . import utils


TEMPLATE = "summary-{dataset_name}"


def _dummy_evolution():
    epochs = defaultdict(int)
    evolution = []
    for i in range(100):
        x = [int(random.random() * 1000)]
        y = [random.random()]
        epochs[x[-1]] = max(epochs[x[-1]], y[-1])
        for i in range(100):
            x.append(x[-1] + 1)
            y.append(y[-1] + random.random())
            epochs[x[-1]] = max(epochs[x[-1]], y[-1])

        evolution.append((x[0], max(y)))

    x = [0]
    y = [0]
    for i in range(1, 1000):
        x.append(i)
        y.append(max(epochs[i], y[-1]))

    return [(x, y)]


def get_id(dataset_name):
    return TEMPLATE.format(dataset_name=dataset_name)


SIGNAL_ID = 'summary-signal'


def build(redis_client, dataset_name, model_names):
    print(get_id(dataset_name))
    return dcc.Graph(id=get_id(dataset_name),
                     figure=render(redis_client, dataset_name, model_names),
                     clear_on_unhover=False)  # True)


def render(redis_client, dataset_name, model_names, *args, distrib_mode=None):

    distrib_name = redis_client.get('distrib-name').decode('utf-8')

    key = 'summary-{dataset_name}-{distrib_name}-data'.format(
        dataset_name=dataset_name, distrib_name=distrib_name)

    dataraw = redis_client.get(key)

    # TODO: Check timestamp to avoid updating if there is no changes
    #       *Only check if the render is triggered by n_interval and not by user click

    if dataraw is not None:
        data = json.loads(dataraw.decode('utf-8'))['data']
    else:
        data = {}

    return {
        'data': [
            go.Violin(
                x=([model_name for _ in range(len(data[model_name]))]
                   if model_name in data else [model_name]),
                y=([value for value in data[model_name].values()] 
                   if model_name in data else []),
                points='all',
                pointpos=-1.1,
                jitter=0,
                showlegend=False,
                box=dict(visible=True)
                ) for model_name in config.model_names],
        'layout': dict(
            title='models ({})'.format(distrib_name),
            autosize=True,
            height=250,
            font=dict(color='#CCCCCC'),
            titlefont=dict(color='#CCCCCC', size='14'),
            margin=dict(
                l=35,
                r=35,
                b=35,
                t=45
            ),
            hovermode="closest",
            plot_bgcolor="#191A1A",
            paper_bgcolor="#020202",
        )}


def signal(redis_client, dataset_name, model_names, *click_datas):
    # Find what model it is
    print('hillo')
    print('hillo', dataset_name, model_names, *click_datas)
    model_name = None
    for click_data in click_datas:
        if click_data is not None:
            model_name = click_data['points'][0]['x']
            break

    if model_name is None:
        print('model is None prevent update')
        raise dash.exceptions.PreventUpdate

    old_model_name = redis_client.get('model-name').decode('utf-8')

    if old_model_name == model_name:
        print('prevent update')
        raise dash.exceptions.PreventUpdate

    redis_client.set('model-name', model_name)

    print('completed')

    return model_name


"""
summary-dataset-distrib-queue
evo-dataset-model-queue
curves-dataset-model-algo-queue
distrib-dataset-model-algo-queue
"""


class Observer:
    def __init__(self, dataset_name, distrib_name, client):
        self.dataset_name = dataset_name
        self.distrib_name = distrib_name
        self.client = client

    def get_key(self):
        return 'summary-{dataset_name}-{distrib_name}-queue'.format(
            dataset_name=self.dataset_name, distrib_name=self.distrib_name)

    def register(self, document):
        tags = [self.dataset_name, self.distrib_name, 'distrib', 'train']
        if all(tag in document['registry']['tags'] for tag in tags):
            try:
                observed_doc = dict(id=document['id'],
                                    model_name=utils.get_model_name(document['registry']['tags']),
                                    value=document['output']['best']['test']['error_rate'])
                self.client.rpush(self.get_key(), json.dumps(observed_doc))
            except Exception as e:
                print(str(e))
                print('error, skipping {}'.format(document['id']))


def build_observers(redis_client, dataset_names, model_names, algo_names, distrib_names):
    observers = []
    for dataset_name in dataset_names:
        for distrib_name in distrib_names:
            observers.append(Observer(dataset_name, distrib_name, redis_client))

    return observers


class DataProcessor(processor.DataProcessor):

    def compute(self, data, new_data):

        for new_trial in new_data:
            model_name = new_trial['model_name']
            if model_name not in data:
                data[model_name] = dict()
            data[model_name][new_trial['id']] = new_trial['value']

        return data
