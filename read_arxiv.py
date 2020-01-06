#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
here = os.path.dirname(os.path.realpath(__file__))  # script folder
from urllib.request import Request, urlopen
import datetime as dt
from bs4 import BeautifulSoup
import text
import tts
import config
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

S = tts.Speaker()
C = config.load('config.ini')
print(banners.fancy)
print(text.section('Options for read_arxiv.py'))
print(C)
print(text.spacer())

fol = C.folder
URLbase = 'https://arxiv.org'
url = f'{URLbase}/list/{C.areas}/new'
today = dt.datetime.now().date()
fname = f"{C.folder_html}/{today.strftime('%y%m.%d')}.arxiv"

try:
   titles,sections = parse_arxiv(fname)
   S.say('Loaded papers from local arXiv copy')
except FileNotFoundError:
   os.system('./arxiv.py')
   titles,sections = parse_arxiv(fname)
for title,section in zip(titles,sections):
   S.say(title)
   # section = sorted(section,key=lambda x:len(x.abstract))
   for i_entry in range(len(section)):
      entry = section[i_entry]
      S.say(f'{i_entry+1}th entry')
      print(text.title(entry.title,s='~'))
      txt = f'Title: {entry.title}'
      S.say(txt,prtxt=False)
      resp = S.ask4input('Continue to read the abstract?.\n1 for yes, 2 for no\n')
      if resp == '1':
         print(text.paragraph(entry.abstract))
         txt = f'Abstract: {entry.abstract}.'   # XXX Clean inline tex here
         S.say(txt,prtxt=False)
         resp = S.ask4input('Download the paper?,\n1 for yes; 2 for no\n')
         if resp == '1':
            download_paper(entry.ID, fol=fol)
            txt = ['Read paper now, or save for later?.',
                   '1 for now, 2 for later']
            resp = S.ask4input('\n'.join(txt))
            if resp == '1':
               S.read_paper(entry.ID,folder=fol)
            else:
               with open('to-read.txt','a') as f:
                  f.write(f'{entry.ID}\n')
      else:
         exit()
         say('Continuing')

S.say(f'Congratulations you finished checking all {len(sections[0])} papers')
S.say('Proceed with pending reading:')
for arxivID in open('to-read.txt','r').read().strip().splitlines():
   S.read_paper(arxivID,folder=C.folder)
