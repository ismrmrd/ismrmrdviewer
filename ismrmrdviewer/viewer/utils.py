from collections import OrderedDict

class CachedDataset :

    def __init__(self, dataset, buffer_size : int = 1024  ):
        self.buffer_size = buffer_size
        self.dataset = dataset
        self.buffer = OrderedDict()

    def __getitem__(self, key):

        if key in self.buffer:
            acq = self.buffer[key]
            self.buffer.move_to_end(key)
            return acq

        acq = self.dataset[key]
        self.__buffer_value(key,acq)
        return acq

    def __buffer_value(self,key,acq ):
        self.buffer[key] = acq
        if len(self.buffer) > self.buffer_size:
            self.buffer.popitem(last=False)

    def __len__(self):
        return self.dataset.data.size
