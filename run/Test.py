import torch
from torch.nn import modules
import yaml
import os
import argparse
import tqdm
import sys

import torch.nn.functional as F
import numpy as np

from PIL import Image
from easydict import EasyDict as ed

filepath = os.path.split(__file__)[0]
repopath = os.path.split(filepath)[0]
sys.path.append(repopath)

from lib import *
from utils.dataloader import *
from utils.utils import *

def _args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='configs/RIUNet.yaml')
    parser.add_argument('--verbose', action='store_true', default=False)
    return parser.parse_args()

def test(opt):
    model = eval(opt.Model.name)(channels=opt.Model.channels, pretrained=opt.Model.pretrained)
    model.load_state_dict(torch.load(os.path.join(opt.Test.Checkpoint.checkpoint_dir, 'latest.pth')), strict=True)
    model.cuda()
    model.eval()    

    if verbose is True:
        testsets = tqdm.tqdm(opt.Test.Dataset.testsets, desc='Total TestSet', total=len(opt.Test.Dataset.testsets), position=0, bar_format='{desc:<30}{percentage:3.0f}%|{bar:50}{r_bar}')
    else:
        testsets = opt.Test.Dataset.testsets

    for testset in testsets:
        data_path = os.path.join(opt.Test.Dataset.root, testset)
        save_path = os.path.join(opt.Test.Checkpoint.checkpoint_dir, testset)

        os.makedirs(save_path, exist_ok=True)

        test_dataset = eval(opt.Test.Dataset.type)(image_root=os.path.join(opt.Test.Dataset.root, testset, 'images'),
                                              gt_root=os.path.join(opt.Test.Dataset.root, testset, 'masks'),
                                              transform_list=opt.Test.Dataset.transform_list)

        test_loader = data.DataLoader(dataset=test_dataset,
                                      batch_size=1,
                                      num_workers=opt.Test.Dataloader.num_workers,
                                      pin_memory=opt.Test.Dataloader.pin_memory)

        if verbose is True:
            samples = tqdm.tqdm(enumerate(test_loader), desc=testset + ' - Test', total=len(test_loader), position=1, leave=False, bar_format='{desc:<30}{percentage:3.0f}%|{bar:50}{r_bar}')
        else:
            samples = enumerate(test_loader)
            
        for i, sample in samples:
            original_size = sample['original_size']
            name = sample['name']
            
            original_size = (int(original_size[0]), int(original_size[1]))
            out = model(sample['image'].cuda())['pred']
            out = F.interpolate(out, original_size, mode='bilinear', align_corners=True)

            out = out.data.cpu()
            out = torch.sigmoid(out)
            out = out.numpy().squeeze()
            out = (out - out.min()) / (out.max() - out.min() + 1e-8)
            Image.fromarray((out * 255).astype(np.uint8)).save(os.path.join(save_path, name[0]))

if __name__ == "__main__":
    args = _args()
    opt = ed(yaml.load(open(args.config), yaml.FullLoader))
    test(opt, args.verbose)