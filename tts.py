#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import text
import sys, select

class Speaker(object):
   def __init__(self,platform=''):
   # def get_speak(self):
      if platform == '': platform = sys.platform
      if platform == 'linux':
         # self.com = 'espeak'
         # self.com_say = f'{self.com} -v mb-en1'
         self.com = 'flite'
         self.com_say = f'{self.com} --setf duration_stretch=1.25 -voice slt'
         self.com_kill = f'killall {self.com}'
         self.com_ping = 'ogg123 -q /usr/share/sounds/freedesktop/stereo/message-new-instant.oga'
      elif platform == 'darwin':  #XXX
         voice = 'Samantha'
         self.com = 'say'
         self.com_say = f'{self.com} -v {voice}'
         self.com_kill = f'killall {self.com}'  # &> /dev/null'
         self.com_ping = 'afplay /System/Library/Sounds/Ping.aiff'
   def say(self,txts,prtxt=True,T=1):
      """
      This method reads out loud a list of provided sentences implementing
      commandsto skip elements
      """
      if isinstance(txts,str): txts = [txts]
      i = 0
      while i < len(txts):
         txt = txts[i]
         if prtxt: print(text.voice(txt))
         #XXX
         txt = txt.replace('arxiv', 'archive')
         txt = txt.replace('Arxiv', 'archive')
         txt = txt.replace('arXiv', 'archive')
         txt = txt.replace('ArXiv', 'archive')
         com = f'{self.com_say} "{txt}" &'
         os.system(com)
         while isrunning(self.com):
            # What?? from https://stackoverflow.com/a/2904057/12554411
            inp, _, _ = select.select([sys.stdin], [], [], T)
            if inp:  # something has been typed
               #XXX idea: f,j to go to prev,next sentence
               typed = sys.stdin.readline().strip()
               if typed == 'exit': 
                  os.system(self.com_kill)
                  exit()
               elif typed == 'next':
                  # continue to next
                  os.system(self.com_kill)
               elif typed == 'prev':
                  # continue to next
                  os.system(self.com_kill)
                  i -= 2
         i += 1
   def ask4input(self,txt,T=1):
      """
      Ask for user input by reading a sentence and/or the options and waiting
      for the response.
      A ping-like sound will be displayed to indicate the end of the message
      """
      com = f'({self.com_say} "{txt}" && {self.com_ping}) &'
      os.system(com)
      resp = input(txt)
      os.system(self.com_kill+' 2> /dev/null')
      return resp
   def read_paper(self,ID,folder='.'):
      if folder[-1] == '/': folder = folder[:-1]
      fname = '/'.join([folder,ID])
      if os.path.isdir(fname):
         tex_file = os.popen(f'ls {fname}/*.tex').read().strip()
         xml_file = tex_file.replace('.tex','.xml')
         if not os.path.isfile(xml_file):
            # convert to xml
            com = f'latexml --dest={xml_file} {tex_file}'
            com += ' > /dev/null 2> /dev/null'
            os.system(com)
            if not os.path.isfile(xml_file):
               self.say(f'Sorry, I couldnt parse the tex file in {folder}')
         msg = text.read_tex(xml_file)
         print(msg)
         self.say(msg,prtxt=False)
      elif os.path.isfile(fname+'.pdf'):
         os.system(f"evince {fname+'.pdf'}")
      else: print('No sepo')


def isrunning(process):
   """ Checks if a process is running """
   resp = os.popen(f'ps -e | grep {process} | grep -v grep').read().strip()
   if len(resp) == 0: return False
   else: return True

# ## say (mac only)
# def read_text(txt,prtext='',voice='Samantha'):
#    """
#    Use mac's say command to read some text out loud
#    prtext: text to print in screen, usually the same as the provided text
#    voice: voice to use, list available: say -v ?
#    """
#    if len(prtext) > 0: print(prtext)
#    com = 'say'
#    if len(voice) > 0: com += ' -v {voice}'
#    com += f' {txt}'
#    com = f'{com} &'
#    os.system(com)
#    _ = input('ENTER to stop voice')
#    if isrunning('say'): os.system('killall say')

# def ask4input(txt,voice='Samantha'):
#    com = 'say'
#    if len(voice) > 0: com += ' -v {voice}'
#    com += f' {txt}'
#    com += ' && afplay /System/Library/Sounds/Ping.aiff'
#    com = f'({com}) &'
#    os.system(com)
#    return input(txt)





if __name__ == '__main__':
   S = Speaker()
   resp = S.ask4input('1 for exit, 2 for continue')
   if resp == '1': exit()
   txt = ['Although the importance of AF correlations and Mottness is stressed by various studies, the exact underlying mechanism of the PG is still an open question.',
          'It is natural to expect that long-range AF fluctuations can cause a PG due to the coupling of the electrons to collective magnetic modes.',
          'In hole-doped cuprates, however, this picture does not apply, as the correlation length is significantly reduced.',
          'To shed light on the role played by AF correlations and Mottness, we address in this work the following fundamental question: do all doped Mott insulators with short-range AF correlations have a PG in two dimensions?']
   S.say(txt)
   #print('-- tex ------------------------')
   #read_paper('2001.00019','/home/n03l/belen/papers')
