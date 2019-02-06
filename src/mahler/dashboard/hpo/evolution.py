from collections import defaultdict
import random

import dash_core_components as dcc
import plotly.graph_objs as go


TEMPLATE = "evolution-{dataset_name}"


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


def render(dataset_name, model_names, *args, model_focus=None, algorithm=None):
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
                title='lenet',
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
