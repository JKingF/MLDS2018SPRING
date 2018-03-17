import os
import math
import shutil
import torch
from tqdm import tqdm
from utils.util import ensure_dir


class BaseTrainer:
    def __init__(self, model, loss, metrics, optimizer, epochs,
                 save_dir, save_freq, resume, verbosity, identifier='', logger=None):
        self.model = model
        self.loss = loss
        self.metrics = metrics
        self.optimizer = optimizer
        self.epochs = epochs
        self.save_dir = save_dir
        self.save_freq = save_freq
        self.verbosity = verbosity
        self.identifier = identifier
        self.logger = logger
        self.min_loss = math.inf
        self.start_epoch = 1
        ensure_dir(save_dir)
        if resume:
            self._resume_checkpoint(resume)

    def train(self):
        for epoch in range(self.start_epoch, self.epochs+1):
            result = self._train_epoch(epoch)
            if epoch % self.save_freq == 0:
                self._save_checkpoint(epoch, result[0])
            if self.logger:
                log = {
                    'epoch': epoch,
                    'loss': result[0]
                }
                for i, metric in enumerate(self.metrics):
                    log[metric.__name__] = result[1][i]
                self.logger.add_entry(log)
                if self.verbosity >= 1:
                    print(log)

    def _train_epoch(self, epoch):
        raise NotImplementedError

    def _save_checkpoint(self, epoch, loss):
        if loss < self.min_loss:
            self.min_loss = loss
        arch = type(self.model).__name__
        state = {
            'epoch': epoch,
            'logger': self.logger,
            'arch': arch,
            'state_dict': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'min_loss': self.min_loss,
        }
        filename = os.path.join(self.save_dir,
                                self.identifier + 'checkpoint_epoch{:02d}_loss_{:.5f}.pth.tar'.format(epoch, loss))
        print("Saving checkpoint: {} ...".format(filename))
        torch.save(state, filename)
        if loss == self.min_loss:
            shutil.copyfile(filename, os.path.join(self.save_dir, self.identifier + 'best.pth.tar'))

    def _resume_checkpoint(self, resume_path):
        print("Loading checkpoint: {} ...".format(resume_path))
        checkpoint = torch.load(resume_path)
        self.start_epoch = checkpoint['epoch'] + 1
        self.min_loss = checkpoint['min_loss']
        self.model.load_state_dict(checkpoint['state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        print("Checkpoint '{}' (epoch {}) loaded".format(resume_path, self.start_epoch))
