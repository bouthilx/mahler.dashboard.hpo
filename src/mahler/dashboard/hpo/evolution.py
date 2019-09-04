from collections import defaultdict
import bisect
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

    return {
            'data': [
                go.Scatter(
                    x=data.get(algo_name, {}).get('x', []),
                    y=data.get(algo_name, {}).get('y', []),
                    mode='lines',
                    name=algo_name,
                    # line=dict(color='#FFAA00'),
                    opacity=1.0,
                    showlegend=False,
                    ) for algo_name in config.algo_names],
            'layout': dict(
                yaxis=dict(
                    autorange=True,
                    type='log'),
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

def signal(redis_client, dataset_name, model_names, *click_datas, algo_names=config.algo_names):
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
        # tags = [self.dataset_name, self.model_name, 'hpo', 'train']
        tags = [self.dataset_name, self.model_name, 'train']

        if all(tag in document['registry']['tags'] for tag in tags):
            if 'distrib' in document['registry']['tags'] or 'seed' in document['registry']['tags']:
                return
            # started_on = utils.convert_strdatetime(document['registry']['started_on'])
            try:
                
                observed_doc = dict(id=document['id'],
                                    duration=document['registry']['duration'],
                                    started_on = str(document['registry']['started_on']),
                                    algo_name=utils.get_algo_name(document['registry']['tags']),
                                    value=document['output']['best']['valid']['error_rate'])
                self.client.rpush(self.get_key(), json.dumps(observed_doc))
            except Exception as e:
                print(str(e))
                print('error, skipping {}'.format(document['id']))



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

        for algo_name, algo_data in data.items():
            algo_data['ids'] = set(algo_data['indexes'])

        for new_trial in new_data:
            algo_name = new_trial['algo_name']
            if algo_name not in data:
                data[algo_name] = dict(end_times=[], values=[], durations=[], ids=set(), indexes=[])

            # May be an update to running trial, and not a totally new trial
            if new_trial['id'] in data[algo_name]['ids']:
                index = data[algo_name]['indexes'].index(new_trial['id'])
                del data[algo_name]['indexes'][index]
                del data[algo_name]['end_times'][index]
                del data[algo_name]['values'][index]
                del data[algo_name]['durations'][index]
                data[algo_name]['ids'].remove(new_trial['id'])

            started_on = utils.convert_strdatetime(new_trial['started_on'])
            end_time = str(started_on + datetime.timedelta(seconds=new_trial['duration']))

            index = bisect.bisect_right(data[algo_name]['end_times'], end_time)
            data[algo_name]['ids'].add(new_trial['id'])
            data[algo_name]['indexes'].insert(index, new_trial['id'])
            data[algo_name]['end_times'].insert(index, end_time)
            data[algo_name]['values'].insert(index, new_trial['value'])
            data[algo_name]['durations'].insert(index, new_trial['duration'])

        for algo_name, algo_data in data.items():
            mean_duration = sum(algo_data['durations']) / len(algo_data['durations'])
            duration = []
            evolution = []
            worker_pool = []
            for y in algo_data['values']:
                if len(worker_pool) < config.max_ressource:
                    worker_pool.append(y)
                elif not evolution:
                    duration.append(mean_duration)
                    evolution.append(min(worker_pool))
                    worker_pool = []
                else:
                    duration.append(duration[-1] + mean_duration)
                    evolution.append(min(worker_pool + [evolution[-1]]))
                    worker_pool = []

            algo_data['x'] = duration
            algo_data['y'] = evolution
            algo_data.pop('ids')

        return data
