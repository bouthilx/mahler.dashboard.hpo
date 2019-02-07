import dash
import dash_html_components as html

from flask_caching import Cache


from . import layout
from . import callback



external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def build(options):
    cache, redis_client = build_cache(app, {})

    callbacks_component = callback.build(redis_client, dataset_names=options['dataset_names'],
                                         model_names=options['model_names'])

    layout_component = layout.build(redis_client, dataset_names=options['dataset_names'],
                                    model_names=options['model_names'])
    
    app.layout = html.Div([layout_component, callbacks_component])

    callback.register(app, redis_client, options['dataset_names'], options['model_names'])

    return app


def build_cache(app, options):
    CACHE_CONFIG = {
        'CACHE_TYPE': 'redis',
        'CACHE_KEY_PREFIX': 'fcache',
        'CACHE_REDIS_HOST': 'localhost',
        'CACHE_REDIS_PORT': '6379',
        'CACHE_REDIS_URL': 'redis://localhost:6379'
    }
    cache = Cache()
    cache.init_app(app.server, config=CACHE_CONFIG)

    redis_client = next(iter(cache.app.extensions['cache'].values()))._client

    return cache, redis_client
