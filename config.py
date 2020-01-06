#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
from configparser import ConfigParser, ExtendedInterpolation
from os.path import expanduser
import tts

class Configuration(object):
   def __init__(self,folder,folder_html, voice, func, areas, sects):
      self.folder = folder   # directory to store papers
      self.folder_html = folder_html   # directory to store arxivs html code
      self.voice = voice
      self.tts = func
      self.areas = areas
      self.sections = sects
      for fol in [self.folder,self.folder_html]:
         os.system(f'mkdir -p {fol}')
   def __str__(self):
      txt =  [f'Folder  : {self.folder}']
      txt += [f'Folder (html): {self.folder_html}']
      txt += [f'Voice   : {self.voice}']
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
   voice = config['run']['voice']
   tts_func = config['run']['tts']
   # funcs = {'gtts':tts.read_text, 'ttsx': tts.read_text2,
   #          'espeak':tts.read_text3, 'mac':tts.read_text4}
   funcs = {'mac':tts.read_text}
   tts_func = funcs[tts_func]
   areas = config['web']['areas']
   sections = config['web']['sections']
   return Configuration(folder,folder_html,voice,tts_func,areas,sections)
