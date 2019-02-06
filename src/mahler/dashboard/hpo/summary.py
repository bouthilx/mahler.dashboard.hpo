from collections import defaultdict
import random

import dash_core_components as dcc
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


def build(dataset_name, model_names):
    return dcc.Graph(id=get_id(dataset_name), figure=render(dataset_name, model_names))


def render(dataset_name, model_names, *args, distrib_mode=None):
    print(dataset_name, model_names, args)
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
            title='models',
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
