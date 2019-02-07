import dash
import dash_html_components as html

from . import layout
from . import callback



external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def build(options):
    layout_component = layout.build(dataset_names=options['dataset_names'],
                                    model_names=options['model_names'])
    callbacks_component = callback.build(dataset_names=options['dataset_names'],
                                         model_names=options['model_names'])
    
    app.layout = html.Div([layout_component, callbacks_component])

    callback.register(app, options['dataset_names'], options['model_names'])

    return app
