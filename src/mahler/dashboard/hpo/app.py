import functools

import dash
from dash.dependencies import Input, Output, State

from . import layout
from . import curves
from . import distrib
from . import evolution
from . import summary


external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def build(options):
    app.layout = layout.build(dataset_names=options['dataset_names'],
                              model_names=options['model_names'])

    callbacks(app, options['dataset_names'], options['model_names'])

    return app


def callback(plotters, render, dataset_name, model_names, n_intervals, *clicks):
    if any(clicks):
        # Get which plotter
        index = [i for i, click in enumerate(clicks) if click is not None][0]
        metadata = plotters[index].get_metadata(click_data)
    else:
        metadata = dict()
    return render(dataset_name, model_names, **metadata)


# if click, set options in redis db, when done, signal to all plots.


def callbacks(app, dataset_names, model_names):

    inputs = [Input('interval-component', 'n_intervals'),
              Input('signal-component', 'signal')]

    for dataset_name in dataset_names:
        for plot in [distrib, curves, evolution, summary]:
            print(model_names)
            app.callback(Output(plot.get_id(dataset_name), 'figure'), inputs)(
                            functools.partial(callback, plot.render, dataset_name, model_names))

    # All plots callback to signal callback, function detects which plotter, set db and 
    # then signal

    # click model -> evo, curves, distrib
    # click algo -> curves distrib
    # click distrib -> summary

    for dataset_name in dataset_names:
        for plot in [distrib, curves, evolution, summary]:
            print(model_names)
            app.callback(Output(plot.get_id(dataset_name), 'figure'), inputs)(
                            functools.partial(callback, plot.render, dataset_name, model_names))
