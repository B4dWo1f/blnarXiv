#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
here = os.path.dirname(os.path.realpath(__file__))  # script folder
from urllib.request import Request, urlopen
import datetime as dt
from bs4 import BeautifulSoup
import text
import tts
import console
from arxiv import parse_arxiv, download_paper
import banners


import logging
fmt = '%(asctime)s-%(name)-s-%(levelname)-s-%(message)s'
logging.basicConfig(level=logging.DEBUG,
                  format=fmt, datefmt='%Y/%m/%d-%H:%M',
                  filename=here+'/read_arxiv.log', filemode='a')
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(name)s: %(levelname)s %(message)s')
sh.setFormatter(fmt)
logging.getLogger('').addHandler(sh)
LG = logging.getLogger('main')

import config
C = config.load('config.ini')
print(banners.fancy)
print(C)

fol = C.folder
URLbase = 'https://arxiv.org'
url = f'{URLbase}/list/{C.areas}/new'
today = dt.datetime.now()
today = today.date()
fname = here + '/data/' + today.strftime('%y%m.%d') + '.arxiv'
say = C.tts #tts.read_text4

try: titles,sections = parse_arxiv(fname)
except FileNotFoundError:
   say('Downloading today\'s papers')
   os.system('./arxiv.py')
   titles,sections = parse_arxiv(fname)
for title,section in zip(titles,sections):
   say(title.replace('*','').strip())
   for entry in section:
      print('*'*console.getTerminalSize()[0])
      txt = f'Title: {entry.title}'
      say(txt,prtext=text.title(entry.title))
      resp = tts.ask4input('Continue to read the abstract?.\n1 for yes, 2 for no')
      if resp == '1':
         txt = f'Abstract: {entry.abstract}.'
         say(txt,prtext=text.paragraph(entry.abstract))
         resp = tts.ask4input('Download the paper?,\n1 for yes; 2 for no\n')
         if resp == '1':
            download_paper(entry.ID, fol=fol)
            txt = ['Read paper now, or save for later?.',
                   '1 for now, 2 for later']
            resp = tts.ask4input('\n'.join(txt))
            if resp == '1':
               tts.read_paper(entry.ID,folder=fol)
            else:
               with open('to-read.txt','a') as f:
                  f.write(f'{entry.ID}\n')
      else: say('Continuing')
