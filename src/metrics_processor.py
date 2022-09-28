class ProbeResults(object):

    def __init__(self, metadata={}):
        self.metadata = metadata

    def record_health(self, url, record: bool):
        self.metadata[url]['brpc_health'] = record

    def record_head_count(self, url, record: int):
        self.metadata[url]['brpc_head_count'] = record

    def record_disconnects(self, url, record: int):
        self.metadata[url]['brpc_disconnects'] = record

    def record_latency(self, url, record: float):
        self.metadata[url]['brpc_latency'] = record

    def record_block_height(self, url, record: int):
        self.metadata[url]['brpc_block_height'] = record

    def record_total_difficulty(self, url, record: int):
        self.metadata[url]['brpc_total_difficulty'] = record

    def record_difficulty(self, url, record: int):
        self.metadata[url]['brpc_difficulty'] = record

    def record_gas_price(self, url, record: float):
        self.metadata[url]['brpc_gas_price'] = record

    def record_max_priority_fee(self, url, record: float):
        self.metadata[url]['brpc_max_priority_fee'] = record

    def record_client_version(self, url, record: str):
        self.metadata[url]['brpc_client_version'] = record

    def register(self, url, label_values):
        self.metadata[url] = {
            'brpc_health': None,
            'brpc_head_count': None,
            'brpc_disconnects': None,
            'brpc_latency': None,
            'brpc_block_height': None,
            'brpc_difficulty': None,
            'brpc_total_difficulty': None,
            'brpc_gas_price': None,
            'brpc_max_priority_fee': None,
            'brpc_client_version': None,
            'label_values': label_values
        }

    def get_highest_block(self):
        highest_block = 0
        for url in self.metadata:
            if 'brpc_block_height' in self.metadata[url]:
                if self.metadata[url]['brpc_block_height'] > highest_block:
                    highest_block = self.metadata[url]['brpc_block_height']
        return highest_block

    def get_highest_total_difficulty(self):
        highest_total_difficulty = 0
        for url in self.metadata:
            if 'brpc_total_difficulty' in self.metadata[url]:
                if self.metadata[url]['brpc_total_difficulty'] > highest_total_difficulty:
                    highest_total_difficulty = self.metadata[url]['brpc_total_difficulty']
        return highest_total_difficulty

    def write_metrics(self, metrics):
        highest_block = self.get_highest_block()
        highest_total_difficulty = self.get_highest_total_difficulty()
        try:
            for url in self.metadata:
                if self.metadata[url]['brpc_health'] != None:
                    metrics['brpc_health'].add_metric(self.metadata[url]['label_values'],
                                                      self.metadata[url]['brpc_health'])
                if self.metadata[url]['brpc_head_count'] != None:
                    metrics['brpc_head_count'].add_metric(self.metadata[url]['label_values'],
                                                          self.metadata[url]['brpc_head_count'])
                if self.metadata[url]['brpc_disconnects'] != None:
                    metrics['brpc_disconnects'].add_metric(self.metadata[url]['label_values'],
                                                           self.metadata[url]['brpc_disconnects'])
                if self.metadata[url]['brpc_latency'] != None:
                    metrics['brpc_latency'].add_metric(self.metadata[url]['label_values'],
                                                       self.metadata[url]['brpc_latency'])
                if self.metadata[url]['brpc_block_height'] != None:
                    metrics['brpc_block_height'].add_metric(self.metadata[url]['label_values'],
                                                            self.metadata[url]['brpc_block_height'])
                    behind_highest = highest_block - self.metadata[url]['brpc_block_height']
                    metrics['brpc_block_height_behind_highest'].add_metric(self.metadata[url]['label_values'],
                                                                           behind_highest)
                if self.metadata[url]['brpc_total_difficulty'] != None:
                    metrics['brpc_total_difficulty'].add_metric(self.metadata[url]['label_values'],
                                                                self.metadata[url]['brpc_total_difficulty'])
                    behind_highest_total_difficulty = highest_total_difficulty - self.metadata[url][
                        'brpc_total_difficulty']
                    metrics['brpc_difficulty_behind_highest'].add_metric(self.metadata[url]['label_values'],
                                                                         behind_highest_total_difficulty)

                if self.metadata[url]['brpc_difficulty'] != None:
                    metrics['brpc_difficulty'].add_metric(self.metadata[url]['label_values'],
                                                          self.metadata[url]['brpc_difficulty'])
                if self.metadata[url]['brpc_gas_price'] != None:
                    metrics['brpc_gas_price'].add_metric(self.metadata[url]['label_values'],
                                                         self.metadata[url]['brpc_gas_price'])
                if self.metadata[url]['brpc_gas_price'] != None:
                    metrics['brpc_max_priority_fee'].add_metric(self.metadata[url]['label_values'],
                                                                self.metadata[url]['brpc_max_priority_fee'])
                if self.metadata[url]['brpc_client_version'] != None:
                    metrics['brpc_client_version'].add_metric(
                        self.metadata[url]['label_values'],
                        value={"client_version": self.metadata[url]['brpc_client_version']})
            self.metadata.clear()
        except Exception as e:
            print(e, type(e))
        self.metadata.clear()


results = ProbeResults()
