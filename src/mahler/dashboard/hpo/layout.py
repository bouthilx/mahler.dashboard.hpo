# import mahler.dashboard.hpo.summary as summary
# import mahler.dashboard.hpo.evo as evo
# import mahler.dashboard.hpo.curves as curves
# import mahler.dashboard.hpo.hpi as hpi

import dash_core_components as dcc
import dash_html_components as html

from . import summary
from . import evolution
from . import curves
from . import distrib


def build_row(redis_client, dataset_name, model_names):
    return html.Div([
        html.Div(
            summary.build(redis_client, dataset_name, model_names),
            className='three columns'),
        html.Div(
            evolution.build(redis_client, dataset_name, model_names),
            className='three columns'),
        html.Div(
            curves.build(redis_client, dataset_name, model_names),
            className='three columns'),
        html.Div(
            distrib.build(redis_client, dataset_name, model_names),
            className='three columns')],
        className='row')


def build(redis_client, dataset_names, model_names, refresh_interval=5):
    print(dataset_names)
    rows = [
        dcc.Interval(
            id='interval-component',
            interval=refresh_interval * 1000,
            n_intervals=0)]

    for dataset_name in dataset_names:
        rows.append(build_row(redis_client, dataset_name, model_names))

    return html.Div(rows)
