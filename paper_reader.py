#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import config
import tts

C = config.load('config.ini')

ID = '2001.01393'
S = tts.Speaker()
print(ID,C.folder)
S.read_paper(ID,C.folder)
