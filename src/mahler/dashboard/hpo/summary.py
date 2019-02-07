from collections import defaultdict
import random

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


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


def build(dataset_name, model_names):
    return dcc.Graph(id=get_id(dataset_name), figure=render(dataset_name, model_names),
                     clear_on_unhover=True)


def render(dataset_name, model_names, *args, distrib_mode=None):
    if len(args) == 2:
        n_intervals, distrib_name = args
    else:
        distrib_name = 'min'

    return {
        'data': [
            go.Violin(
                x=[model_name for _ in range(10)],
                y=[random.random() for i in range(10)],
                points='all',
                pointpos=-1.1,
                jitter=0,
                showlegend=False,
                box=dict(visible=True)
                ) for model_name in model_names],
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


def signal(dataset_name, model_names, *click_datas):
    # Find what model it is
    model_name = None
    for click_data in click_datas:
        if click_data is not None:
            model_name = click_data['points'][0]['x']
            break

    if model_name is None:
        return False

    # if already in db: return False
    # else
    # set in DB
    return model_name  # True
