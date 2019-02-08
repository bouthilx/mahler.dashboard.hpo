from collections import defaultdict
import datetime
import random
import time

import json

import dash
import dash_core_components as dcc
import plotly.graph_objs as go

from . import config
from . import processor
from . import utils


TEMPLATE = "evolution-{dataset_name}"


def _dummy_evolution():
    evolutions = []
    for i in range(4):
        epochs = defaultdict(int)
        evolution = []
        for i in range(10):
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

        evolutions.append((x, y))

    return evolutions


def get_id(dataset_name):
    return TEMPLATE.format(dataset_name=dataset_name)


def build(redis_client, dataset_name, model_names):
    return dcc.Graph(id=get_id(dataset_name),
                     figure=render(redis_client, dataset_name, model_names))


def render(redis_client, dataset_name, model_names, *args, model_focus=None, algorithm=None):

    model_name = redis_client.get('model-name').decode('utf-8')

    key = 'evolution-{dataset_name}-{model_name}-data'.format(
        dataset_name=dataset_name, model_name=model_name)

    dataraw = redis_client.get(key)

    if dataraw is not None:
        data = json.loads(dataraw.decode('utf-8'))['data']
    else:
        data = {}

    lines = dict()
    for algo_name in config.algo_names:
        lines[algo_name] = ([], [])

        for trial in sorted(data.get(algo_name, {}).values(), key=lambda trial: trial[0]):
            lines[algo_name][0].append(trial[0])
            lines[algo_name][1].append(trial[1])

    return {
            'data': [
                go.Scatter(
                    x=lines[algo_name][0],
                    y=lines[algo_name][1],
                    mode='lines',
                    name=algo_name,
                    # line=dict(color='#FFAA00'),
                    opacity=1.0,
                    showlegend=False,
                    ) for algo_name in config.algo_names],
            'layout': dict(
                title=model_name,
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


SIGNAL_ID = 'evolution-signal'

__TMP_ALGOS = ['random-search', 'ASHA', 'BO', 'evo']

def signal(redis_client, dataset_name, model_names, *click_datas, algo_names=__TMP_ALGOS):
    # Find what model it is
    algo_name = None
    for click_data in click_datas:
        if click_data is not None:
            algo_name = algo_names[click_data['points'][0]['curveNumber']]
            break

    if algo_name is None:
        raise dash.exceptions.PreventUpdate

    old_algo_name = redis_client.get('algo-name').decode('utf-8')

    if old_algo_name == algo_name:
        raise dash.exceptions.PreventUpdate

    redis_client.set('algo-name', algo_name)

    return algo_name


class Observer:
    def __init__(self, dataset_name, model_name, client):
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.client = client

    def get_key(self):
        return 'evolution-{dataset_name}-{model_name}-queue'.format(
            dataset_name=self.dataset_name, model_name=self.model_name)

    def register(self, document):
        tags = [self.dataset_name, self.model_name, 'hpo', 'train']
        if all(tag in document['registry']['tags'] for tag in tags):
            start_time = utils.convert_strdatetime(document['registry']['start_time'])
            duration = datetime.timedelta(seconds=document['registry']['duration'])

            observed_doc = dict(id=document['id'],
                                end_time=str(start_time + duration),
                                algo_name=utils.get_algo_name(document['registry']['tags']),
                                value=document['output']['best_stats']['valid']['error_rate'])
            self.client.rpush(self.get_key(), json.dumps(observed_doc))


def build_observer(dataset_name, model_name, algo_name, distrib_name, redis_client):
    return Observer(dataset_name, model_name, algo_name, distrib_name, redis_client)


def build_observers(redis_client, dataset_names, model_names, algo_names, distrib_names):
    observers = []
    for dataset_name in dataset_names:
        for model_name in model_names:
            observers.append(Observer(dataset_name, model_name, redis_client))

    return observers


class DataProcessor(processor.DataProcessor):

    def compute(self, data, new_data):

        for new_trial in new_data:
            algo_name = new_trial['algo_name']
            if algo_name not in data:
                data[algo_name] = dict()
            data[algo_name][new_trial['id']] = (new_trial['end_time'], new_trial['value'])

        return data
