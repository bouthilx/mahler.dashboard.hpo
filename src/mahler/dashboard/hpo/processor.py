import datetime
import multiprocessing
import time

import json


class DataProcessor(multiprocessing.Process):
    daemon = True

    def __init__(self, observer, max_pop=50, sleep_time=1, **kwargs):
        self.observer = observer
        self.max_pop = max_pop
        self.sleep_time = sleep_time
        super(DataProcessor, self).__init__(**kwargs)

    def run(self):
        client = self.observer.client

        while True:
            time.sleep(self.sleep_time)

            new_data = []
            for i in range(self.max_pop):
                rval = client.blpop(self.observer.get_key(), timeout=5)
                if rval is None:
                    break

                new_data.append(json.loads(rval[1].decode('utf-8')))

            if not new_data:
                continue

            data_key = self.observer.get_key().replace('-queue', '-data')
            dataraw = client.get(data_key)
            if dataraw is not None:
                data = json.loads(dataraw.decode('utf-8'))['data']
            else:
                data = {}

            data = {'data': self.compute(data, new_data), 'timestamp': str(datetime.datetime.now())}
            client.set(data_key, json.dumps(data))

    def compute(self):
        raise NotImplemented
