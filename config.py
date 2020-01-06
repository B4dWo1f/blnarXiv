#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
from configparser import ConfigParser, ExtendedInterpolation
from os.path import expanduser
import tts

class Configuration(object):
   def __init__(self,folder,folder_html, areas, sects):
      self.folder = folder   # directory to store papers
      self.folder_html = folder_html   # directory to store arxivs html code
      self.areas = areas
      self.sections = sects
      for fol in [self.folder,self.folder_html]:
         os.system(f'mkdir -p {fol}')
   def __str__(self):
      txt =  [f'Folder  : {self.folder}']
      txt += [f'Folder (html): {self.folder_html}']
      txt += [f'Areas   : {self.areas}']
      txt += [f'Sections: {self.sections}']
      return '\n'.join(txt)

def load(fname):
   if not os.path.isfile(fname): return None
   config = ConfigParser(inline_comment_prefixes='#')
   config._interpolation = ExtendedInterpolation()
   config.read(fname)
   folder = expanduser(config['sys']['folder'])
   folder_html = expanduser(config['sys']['folder_html'])
   areas = config['web']['areas']
   sections = config['web']['sections']
   return Configuration(folder,folder_html,areas,sections)
