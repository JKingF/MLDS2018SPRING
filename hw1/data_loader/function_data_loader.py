import random
import numpy as np
import matplotlib.pyplot as plt
from base.base_data_loader import BaseDataLoader


class FunctionDataLoader(BaseDataLoader):
    def __init__(self, target_func, batch_size, n_sample, x_range, shuffle=True):
        super(FunctionDataLoader, self).__init__(batch_size)
        self.batch_size = batch_size
        self.n_batch = n_sample // batch_size
        self.x_range = x_range
        self.shuffle = shuffle
        if target_func == 'sin':
            self.target_func = lambda x: np.sin(4*np.pi*x)
        elif target_func == 'sinc':
            self.target_func = lambda x: np.sin(4*np.pi*x) / (4*np.pi*x + 1e-10)
        elif target_func == 'stair':
            self.target_func = lambda x: (np.ceil(4*x) - 2.5) / 1.5
        elif target_func == 'square':
            self.target_func = lambda x: np.sign(np.cos(8*np.pi*x))
        elif target_func == 'damp':
            self.target_func = lambda x: 10*np.sqrt(x)*np.exp(-8*x) * np.sin(6*np.pi*(x-0.25))
        else:
            self.target_func = None
        self.x = np.array([i for i in np.linspace(self.x_range[0], self.x_range[1],
                                                  self.n_batch * self.batch_size)])
        self.y = np.array([self.target_func(i) for i in self.x])
        self.batch_idx = 0

    def __iter__(self):
        self.n_batch = len(self.x) // self.batch_size
        self.batch_idx = 0
        assert self.n_batch > 0
        if self.shuffle:
            rand_idx = np.random.permutation(len(self.x))
            self.x = np.array([self.x[i] for i in rand_idx])
            self.y = np.array([self.y[i] for i in rand_idx])
        return self

    def __next__(self):
        if self.batch_idx < self.n_batch:
            x_batch = self.x[self.batch_idx * self.batch_size:(self.batch_idx+1) * self.batch_size]
            y_batch = self.y[self.batch_idx * self.batch_size:(self.batch_idx+1) * self.batch_size]
            x_batch = x_batch.reshape((-1, 1))
            y_batch = y_batch.reshape((-1, 1))
            self.batch_idx = self.batch_idx + 1
            return x_batch, y_batch
        else:
            raise StopIteration

    def __len__(self):
        self.n_batch = len(self.x) // self.batch_size
        return self.n_batch
