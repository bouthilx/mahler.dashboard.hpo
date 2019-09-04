import multiprocessing

from . import config
from . import summary
from . import evolution
from . import curves
from . import distrib


class Observer:
    def get_key(self):
        raise NotImplemented

    def register(self, document):
        raise NotImplemented


def build(redis_client, dataset_names, model_names):
    algo_names = config.algo_names
    distrib_names = config.distrib_names

    observers = []
    for plotter in [summary, evolution, curves, distrib]:
        plotter_observers = plotter.build_observers(
            redis_client, dataset_names, model_names, algo_names, distrib_names)

        for observer in plotter_observers:
            if not hasattr(plotter, 'DataProcessor'):
                break
            p = plotter.DataProcessor(observer=observer)
            p.start()

        observers += plotter_observers

    return observers
