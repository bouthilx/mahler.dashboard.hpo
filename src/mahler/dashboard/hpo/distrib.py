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


TEMPLATE = "distrib-{dataset_name}"


def get_id(dataset_name):
    return TEMPLATE.format(dataset_name=dataset_name)


class DistributionPlot():
    def __init__(self, dataset_name, default_model='lenet', default_algorithm='asha'):
        self.dataset_name = dataset_name
        self.default_model = default_model
        self.default_algorithm = default_algorithm
        self.id = get_id(dataset_name)

    def build(self, redis_client, model_names):
        return dcc.Graph(id=self.id, figure=self.render(redis_client, model_names))

    def compute(data):
        pass
        # smove(src, dst, value)
        # data = get(self.id + "-queue", value)
        # set("{id}-{model}-{algo}-data".format(id=self.id, model=model, algo=algo), value)

    def render(self, redis_client, model_names, *args):

        model_name = redis_client.get('model-name').decode('utf-8')
        algo_name = redis_client.get('algo-name').decode('utf-8')

        key = 'distrib-{dataset_name}-{model_name}-{algo_name}-data'.format(
            dataset_name=self.dataset_name, model_name=model_name, algo_name=algo_name)

        dataraw = redis_client.get(key)
        # print('get', key)
        # print(dataraw)
        # if dataraw is None:
        #     return {}

        # TODO: Check timestamp to avoid updating if there is no changes
        #       *Only check if the render is triggered by n_interval and not by user click

        # print("render summary")

        if dataraw is not None:
            data = json.loads(dataraw.decode('utf-8'))['data']
        else:
            data = {}
        # print(data)


        return {
            'data': [
                go.Violin(
                    x=([distrib_name for _ in range(len(data[distrib_name]))]
                       if distrib_name in data else [distrib_name]),
                    y=([value for value in data[distrib_name].values()] 
                       if distrib_name in data else []),
                    points='all',
                    pointpos=-1.1,
                    jitter=0,
                    showlegend=False,
                    box=dict(visible=True)
                    ) for distrib_name in config.distrib_names],
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


def refresh():
    return


def build(redis_client, dataset_name, model_names):
    return DistributionPlot(dataset_name).build(redis_client, model_names)


def render(redis_client, dataset_name, model_names, *args):
    return DistributionPlot(dataset_name).render(redis_client, model_names, *args)


SIGNAL_ID = 'distrib-signal'


def signal(redis_client, dataset_name, model_names, *click_datas):
    # Find what distrib it is
    distrib_name = None
    for click_data in click_datas:
        if click_data is not None:
            distrib_name = click_data['points'][0]['x']
            break

    if distrib_name is None:
        raise dash.exceptions.PreventUpdate

    old_distrib_name = redis_client.get('distrib-name').decode('utf-8')

    if old_distrib_name == distrib_name:
        raise dash.exceptions.PreventUpdate

    redis_client.set('distrib-name', distrib_name)

    return distrib_name


class Observer:
    def __init__(self, dataset_name, model_name, algo_name, client):
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.algo_name = algo_name
        self.client = client

    def get_key(self):
        return 'distrib-{dataset_name}-{model_name}-{algo_name}-queue'.format(
            dataset_name=self.dataset_name, model_name=self.model_name, algo_name=self.algo_name)

    def register(self, document):
        tags = [self.dataset_name, self.model_name, self.algo_name, 'distrib', 'train']
        if all(tag in document['registry']['tags'] for tag in tags):
            observed_doc = dict(
                id=document['id'],
                distrib_name=utils.get_distrib_name(document['registry']['tags']),
                value=document['output']['best_stats']['test']['error_rate'])
            self.client.rpush(self.get_key(), json.dumps(observed_doc))


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
            distrib_name = new_trial['distrib_name']
            if distrib_name not in data:
                data[distrib_name] = dict()
            # print(new_trial['id'])
            data[distrib_name][new_trial['id']] = new_trial['value']

        return data
