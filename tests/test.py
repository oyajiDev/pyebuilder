# -*- coding: utf-8 -*-
import os, sys
from pyebuilder.builder import build


__dirname = os.path.dirname(os.path.realpath(__file__))
build(os.path.join(__dirname, "test_app"), os.path.join(__dirname, "build"))
