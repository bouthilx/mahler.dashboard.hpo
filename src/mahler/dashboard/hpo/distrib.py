import random

import dash_core_components as dcc
import plotly.graph_objs as go


TEMPLATE = "distrib-{dataset_name}"


def get_id(dataset_name):
    return TEMPLATE.format(dataset_name=dataset_name)


class DistributionPlot():
    def __init__(self, dataset_name, default_model='lenet', default_algorithm='asha'):
        self.dataset_name = dataset_name
        self.default_model = default_model
        self.default_algorithm = default_algorithm
        self.id = get_id(dataset_name)

    def build(self, model_names):
        return dcc.Graph(id=self.id, figure=self.render(model_names))

    def compute(data):
        # smove(src, dst, value)
        data = get(self.id + "-queue", value)
        set("{id}-{model}-{algo}-data".format(id=self.id, model=model, algo=algo), value)

    def render(self, model_names, *args):
        if len(args) == 3:
            n_intervals, model_name, algo_name = args
        else:
            model_name = 'lenet'
            algo_name = 'random-search'

        return {
            'data': [
                go.Violin(
                    x=[label for _ in range(10)],
                    y=[random.random() for i in range(10)],
                    points='all',
                    pointpos=-1.1,
                    jitter=0,
                    showlegend=False,
                    box=dict(visible=True)
                    ) for label in ['min', 'max', 'mean']],
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


def build(dataset_name, model_names):
    return DistributionPlot(dataset_name).build(model_names)


def render(dataset_name, model_names, *args):
    return DistributionPlot(dataset_name).render(model_names, *args)


SIGNAL_ID = 'distrib-signal'


def signal(dataset_name, model_names, *click_datas):
    # Find what distrib it is
    distrib_name = None
    for click_data in click_datas:
        if click_data is not None:
            distrib_name = click_data['points'][0]['x']
            break

    if distrib_name is None:
        return False

    # if already in db: return False
    # else
    # set in DB
    return distrib_name  # True
