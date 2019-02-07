import random

import dash
import dash_core_components as dcc
import plotly.graph_objs as go


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
    return dcc.Graph(id=get_id(dataset_name), figure=render(redis_client, dataset_name, model_names))


def render(redis_client, dataset_name, model_names, *args, model_focus=None, algorithm=None):

    model_name = redis_client.get('model-name').decode('utf-8')
    algo_name = redis_client.get('algo-name').decode('utf-8')

    return {
            'data': [
                go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line=dict(color='#FFAA00'),
                    opacity=1.0,
                    showlegend=False,
                    ) for x, y in _dummy_curves()],
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
