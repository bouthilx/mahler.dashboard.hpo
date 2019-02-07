from collections import defaultdict
import random

import dash_core_components as dcc
import plotly.graph_objs as go


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


def build(dataset_name, model_names):
    return dcc.Graph(id=get_id(dataset_name), figure=render(dataset_name, model_names))


def render(dataset_name, model_names, *args, model_focus=None, algorithm=None):
    # load options from db
    # load data from db based on options (ex: model_name)
    if len(args) == 2:
        n_intervals, model_name = args
    else:
        model_name = 'lenet'
    return {
            'data': [
                go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line=dict(color='#FFAA00'),
                    opacity=1.0,
                    showlegend=False,
                    ) for x, y in _dummy_evolution()],
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

def signal(dataset_name, model_names, *click_datas, algo_names=__TMP_ALGOS):
    # Find what model it is
    algo_name = None
    for click_data in click_datas:
        if click_data is not None:
            algo_name = algo_names[click_data['points'][0]['curveNumber']]
            break

    if algo_name is None:
        return False

    # if already in db: return False
    # else
    # set in DB
    return algo_name  # True
