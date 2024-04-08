#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import numpy as np
from load_xml import load_xml
from ancillary import Ancillary_NASA
from level1 import Level1_base


class Level1_MSI(Level1_base):

    def __init__(self, dirname,
                 ancillary=None):
        '''
        Sentinel-2 MSI Level1 reader

        dirname: granule directory. Examples:
        '''
        self.ancillary = Ancillary_NASA()
        self.date = load_xml(dirname)
        self.init_ancillary()
    def init_ancillary(self):
        self.ozone = self.ancillary.get('ozone', self.date)
        self.wind_speed = self.ancillary.get('wind_speed', self.date)
        self.surf_press = self.ancillary.get('surf_press', self.date)


    def attributes(self, datefmt):
        attr = OrderedDict()
        attr['sensing_time'] = self.date.strftime(datefmt)
        return attr


    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def read_xml_block(item):
    '''
    read a block of xml data and returns it as a numpy float32 array
    '''
    d = []
    for i in item.iterchildren():
        d.append(i.text.split())
    return np.array(d, dtype='float32')


