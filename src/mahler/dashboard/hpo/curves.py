import bisect
import copy
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
                    x=data['x'][trial_id],
                    y=data['y'][trial_id],
                    mode='lines',
                    line=dict(color='#FFAA00'),
                    opacity=1.0,
                    showlegend=False,
                    ) for trial_id in data.get('x', {}).keys()],
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
        # tags = [self.dataset_name, self.model_name, self.algo_name, 'hpo', 'train']
        tags = [self.dataset_name, self.model_name, self.algo_name, 'train']

        if all(tag in document['registry']['tags'] for tag in tags):
            if 'distrib' in document['registry']['tags'] or 'seed' in document['registry']['tags']:
                return

            try:
                observed_doc = dict(
                    id=document['id'],
                    duration=document['registry']['duration'],
                    started_on=str(document['registry']['started_on']),
                    algo_name=utils.get_algo_name(document['registry']['tags']),
                    values=[stats['valid']['error_rate'] for stats in document['output']['all']])

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
            for algo_name in algo_names:
                observers.append(Observer(dataset_name, model_name, algo_name, redis_client))

    return observers


class DataProcessor(processor.DataProcessor):

    def compute(self, data, new_data):

        if not data:
            data = dict(end_times=[], values=[], durations=[], ids=set(), indexes=[])
        else:
            data['ids'] = set(data['indexes'])

        for new_trial in new_data:
            # May be an update to running trial, and not a totally new trial
            if new_trial['id'] in data['ids']:
                index = data['indexes'].index(new_trial['id'])
                del data['indexes'][index]
                del data['end_times'][index]
                del data['values'][index]
                del data['durations'][index]
                data['ids'].remove(new_trial['id'])

            started_on = utils.convert_strdatetime(new_trial['started_on'])
            end_time = str(started_on + datetime.timedelta(seconds=new_trial['duration']))

            index = bisect.bisect_right(data['end_times'], end_time)
            data['ids'].add(new_trial['id'])
            data['indexes'].insert(index, new_trial['id'])
            data['end_times'].insert(index, end_time)
            # Downsample: ignore first and keep last
            data['values'].insert(index, new_trial['values'][4::5])
            data['durations'].insert(index, new_trial['duration'])

        mean_duration = sum(data['durations']) / len(data['durations'])
        duration = []
        pools = []
        worker_pool = []
        for index, trial_id in enumerate(data['ids']):
            if len(worker_pool) < config.max_ressource:
                worker_pool.append(index)
            else:
                duration.append(mean_duration * len(duration))
                pools.append(worker_pool)
                worker_pool = []

        data['x'] = dict()
        data['y'] = dict()
        for start_time, pool in zip(duration, pools):
            for index in pool:
                trial_id = data['indexes'][index]
                trial_duration = data['durations'][index]
                values = data['values'][index]
                duration_per_step = trial_duration / len(values)
                data['x'][trial_id] = [start_time + i * duration_per_step  for i in range(len(values))]
                data['y'][trial_id] = values

        data.pop('ids')

        return data
