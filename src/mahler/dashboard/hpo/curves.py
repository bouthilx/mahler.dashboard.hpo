import datetime
import random
import time

import json

import dash_core_components as dcc
import plotly.graph_objs as go

from . import config
from . import processor
from . import utils


TEMPLATE = "curves-{dataset_name}"


def _dummy_curves():
    curves = []
    for i in range(50):
        x = [random.random() * 1000]
        y = [random.random()]
        for i in range(100):
            x.append(x[-1] + 1)
            y.append(y[-1] + random.random())

        curves.append((x, y))

    return curves


def get_id(dataset_name):
    return TEMPLATE.format(dataset_name=dataset_name)


def build(redis_client, dataset_name, model_names):
    return dcc.Graph(id=get_id(dataset_name),
                     figure=render(redis_client, dataset_name, model_names))


def render(redis_client, dataset_name, model_names, *args, model_focus=None, algorithm=None):

    model_name = redis_client.get('model-name').decode('utf-8')
    algo_name = redis_client.get('algo-name').decode('utf-8')

    key = 'curves-{dataset_name}-{model_name}-{algo_name}-data'.format(
        dataset_name=dataset_name, model_name=model_name, algo_name=algo_name)

    dataraw = redis_client.get(key)

    if dataraw is not None:
        data = json.loads(dataraw.decode('utf-8'))['data']
    else:
        data = {}

    return {
            'data': [
                go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line=dict(color='#FFAA00'),
                    opacity=1.0,
                    showlegend=False,
                    ) for x, y in data.values()],
            'layout': dict(
                title='{} - {}'.format(model_name, algo_name),
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


class Observer:
    def __init__(self, dataset_name, model_name, algo_name, client):
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.algo_name = algo_name
        self.client = client

    def get_key(self):
        return 'curves-{dataset_name}-{model_name}-{algo_name}-queue'.format(
            dataset_name=self.dataset_name, model_name=self.model_name, algo_name=self.algo_name)

    def register(self, document):
        tags = [self.dataset_name, self.model_name, self.algo_name, 'hpo', 'train']
        if all(tag in document['registry']['tags'] for tag in tags):
            self.client.rpush(self.get_key(), json.dumps(document))


def build_observer(dataset_name, model_name, algo_name, distrib_name, redis_client):
    return Observer(dataset_name, model_name, algo_name, distrib_name, redis_client)


def build_observers(redis_client, dataset_names, model_names, algo_names, distrib_names):
    observers = []
    for dataset_name in dataset_names:
        for model_name in model_names:
            for algo_name in algo_names:
                observers.append(Observer(dataset_name, model_name, algo_name, redis_client))

    return observers


class DataProcessor(processor.DataProcessor):

    def compute(self, data, new_data):

        for new_trial in new_data:
            intervals = new_trial['registry']['duration'] / len(new_trial['output']['all_stats'])
            timedeltas = datetime.timedelta(seconds=intervals)
            epochs = []
            for epoch_data in new_trial['output']['all_stats']:
                if epochs:
                    timestamp = epochs[-1][0] + timedeltas
                else:
                    timestamp = utils.convert_strdatetime(new_trial['registry']['start_time'])
                epochs.append((timestamp, epoch_data['valid']['error_rate']))

            data[new_trial['id']] = list(zip(*((str(x), y) for x, y in epochs)))

        return data
