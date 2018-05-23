import os
import json
import logging
import argparse
import torch
from model import *
from model.metric import *
from data_loader import GanDataLoader
from trainer import *
from logger import Logger

logging.basicConfig(level=logging.INFO, format='')


def main(config, resume):
    train_logger = Logger()

    data_loader = GanDataLoader(config)
    valid_data_loader = data_loader.split_validation()
    
    model = eval(config['arch'])(config)
    model.summary()

    metrics = [eval(metric) for metric in config['metrics']]

    eval(config['arch']+'Trainer')(model, None, metrics,
                                   resume=resume,
                                   config=config,
                                   data_loader=data_loader,
                                   valid_data_loader=valid_data_loader,
                                   train_logger=train_logger).train()


if __name__ == '__main__':
    logger = logging.getLogger()

    parser = argparse.ArgumentParser(description='PyTorch Template')
    parser.add_argument('-c', '--config', default=None, type=str,
                        help='config file path (default: None)')
    parser.add_argument('-r', '--resume', default=None, type=str,
                        help='path to latest checkpoint (default: None)')

    args = parser.parse_args()

    config = None
    if args.resume is not None:
        if args.config is not None:
            logger.warning('Warning: --config overridden by --resume')
        config = torch.load(args.resume)['config']
    elif args.config is not None:
        config = json.load(open(args.config))
        path = os.path.join(config['trainer']['save_dir'], config['name'])
        if os.path.exists(path):
            opt = input("Warning: path {} already exists, continue? [y/N] ".format(path))
            if opt.upper() != 'Y':
                exit(1)
    assert config is not None

    main(config, args.resume)
