import functools

import dash_html_components as html
from dash.dependencies import Input, Output, State

from . import curves
from . import distrib
from . import evolution
from . import summary


def build(redis_client, dataset_names, model_names):
    signal_components = []
    for plotter in [summary, evolution, curves, distrib]:
        if not signals(plotter):
            continue

        signal_components.append(
            html.Div(id=plotter.SIGNAL_ID, style={'display': 'none'}))

    redis_client.set('model-name', 'preactresnet18')
    redis_client.set('algo-name', 'asha')
    redis_client.set('distrib-name', 'min')

    return html.Div(signal_components)


def callback(render, dataset_name, model_names, n_intervals, *clicks):
    # if any(clicks):
    #     # Get which plotter
    #     index = [i for i, click in enumerate(clicks) if click is not None][0]
    #     metadata = plotters[index].get_metadata(click_data)
    # else:
    metadata = dict()
    return render(dataset_name, model_names, **metadata)


def signals(plotter):
    return hasattr(plotter, 'signal')

# if click, set options in redis db, when done, signal to all plots.

plotter_signals = {
    summary: ['distrib-signal'],
    evolution: [summary.SIGNAL_ID],
    curves: [summary.SIGNAL_ID, 'evolution-signal'],
    distrib: [summary.SIGNAL_ID, 'evolution-signal']
    }


def wrap_signal(signal, *args, **kwargs):
    if not signal(*args, **kwargs):
        raise PreventUpdate


def register(app, redis_client, dataset_names, model_names):

    inputs = [Input('interval-component', 'n_intervals'),
              Input('signal-component', 'children')]

    # for plot in [distrib, curves, evolution, summary]:
    for plot in [summary]:
        if not signals(plot):
            continue

        # Detect click, set options in DB
        inputs = [Input(plot.get_id(dataset_name), 'hoverData') for dataset_name in dataset_names]
        print([plot.get_id(dataset_name) for dataset_name in dataset_names])

        print('install callback', plot.SIGNAL_ID, plot, dataset_names)
        app.callback(Output(plot.SIGNAL_ID, 'children'), inputs)(
                        functools.partial(plot.signal, redis_client, None, model_names))

    # All plots callback to signal callback, function detects which plotter, set db and 
    # then signal

    # click model: summary -> evo, curves, distrib
    # click algo: evo -> curves distrib
    # click distrib -> summary

    for dataset_name in dataset_names:
        for plot in [distrib, curves, evolution, summary]:
            inputs = [Input('interval-component', 'n_intervals')] + [
                # Input(summary.SIGNAL_ID, 'children')]
                Input(signal_name, 'children') for signal_name in plotter_signals[plot]]
 
            app.callback(Output(plot.get_id(dataset_name), 'figure'), inputs)(
                            functools.partial(plot.render, redis_client, dataset_name, model_names))
