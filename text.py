#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import console
from bs4 import BeautifulSoup
import re
import os


def clean(text):
   """ Remove dummy line breaks and double spaces """
   text = ' '.join(text.split())
   ret_text = ''
   for x in text.split('\n'):
      ret_text += x
      if x[-1] == '.': ret_text += '\n'
      else: ret_text += ' '
   return ret_text.lstrip().rstrip()

def justifyRL(str1,str2,w=0):
   """
     Align string 1 and 2 to the left and right respectively.
     If no width is given, use the width of the console
   """
   if str2 == '': return str1
   if w == 0: X,Y = console.getTerminalSize()
   else: X = w
   total = str1+str2
   while len(total) < X:
      str1 = str1 + ' '
      total = str1+str2
   return total

def center(string):
   """ Center text in the console width """
   X,Y = console.getTerminalSize()
   rest = X - len(string)
   if rest > 0:
      padd = rest//2
      return ' '*padd + string
   else: return string

def title(text):
   """ Pretty print for titles """
   X,Y = console.getTerminalSize()
   msg = '='*X + '\n'
   msg += '\033[1m' +center(text)+ '\033[0m'+'\n'
   msg += '='*X
   return msg

def paragraph(text,W=0):
   """
    Introduce breaklines when printing to avoid splitting words
   """
   if W == 0: W,Y = console.getTerminalSize()
   final_text = ''
   current_sentence = ''
   for w in text.split():
      if len(current_sentence+w) >= W:
         final_text += current_sentence + '\n'
         current_sentence = ''
      else:   
         current_sentence += w + ' '
   return final_text

###############################################################################
## XXX TEX cleaner
def clean_equation(tag):
   return '\n' + clean_tex(tag.find('math').get('tex')) + '\n'

def clean_title(tag):
   """
   substitutes all the <math> tags by its "tex" attribute.
   """
   return 'Title: ' + clean_inline_math(tag).text

def clean_paragraph(tag):
   """
   substitutes all the <math> tags by its "tex" attribute.
   """
   return clean_inline_math(tag).text

def clean_caption(tag):
   """
   substitutes all the <math> tags by its "tex" attribute.
   """
   for t in tag.find_all('tag'):
      t.replaceWith(f' {t.text} ')
   return clean_inline_math(tag).text


def locate_tex_command(string,name,args=1):
   """
   returns the arguments of a given latex command:
   \sin{x} ---> x
   \frac{3}{7} ---> 3,7
   """
   if args == 1: pattern = r'\\%s\{(.*?)\}'%(name)
   elif args == 2:
      pattern = r'\\%s\{(.*?)\}\{(.*?)\}'%(name)
      print('ffffffffff')
      print(string)
      print('^^^^^^^^^^')
   elif args == 3: pattern = r'\\%s\{(.*?)\}\{(.*?)\}\{(.*?)\}'%(name)
   match = re.search(pattern, string)
   return match.groups()


def clean_tex(eq):
   print('===========================')
   eq = eq.replace('%\n','')
   eq = eq.replace('\displaystyle','')
   eq = eq.replace('\\text','')
   eq = eq.replace('\\left','')
   eq = eq.replace('\\right','')
   eq = eq.replace('\\boldsymbol','')
   eq = eq.replace('\mathbf','')
   eq = eq.replace('\\bold','')
   eq = eq.replace('_',', sub ')
   eq = eq.replace('-',' minus ')
   eq = eq.replace('/',' over ')
   eq = eq.replace('*',' star ')
   eq = eq.replace('\perp',' perpendicular ')
   eq = eq.replace('\int',' integral ')
   #XXX verwenza de mis antepasados!!!!
   while '\lx@braket@' in eq:
      inner_brkt = locate_tex_command(eq, 'lx@braket@', 1)
      inner_brkt = inner_brkt[0]
      old = fr'\lx@braket@{{{inner_brkt}}}'
      new = f' braket of {inner_brkt} '
      eq = eq.replace(old, new)
   while r'\frac' in eq:
      print('==> frac',eq)
      num,deno = locate_tex_command(eq, 'frac', 2)
      old = fr'\frac{{{num}}}{{{deno}}}'
      new = f' fraction: {num} over {deno} '
      eq = eq.replace(old, new)
   while r'\sqrt' in eq:
      sqrt = locate_tex_command(eq, 'sqrt', 1)
      sqrt = sqrt[0]
      old = fr'\sqrt{{{sqrt}}}'
      new = f' square root of {sqrt} '
      eq = eq.replace(old, new)
   print('***************************')
   return eq

def clean_sumation(string):
   sumation = ['', '']
   for p,inds in [(r'\\sum\^\{(.*?)\}_\{(.*?)\}',(0,1)),
                  (r'\\sum_\{(.*?)\}\^\{(.*?)\}',(1,0)),
                  (r'\\sum_\{(.*?)\}',(1,)),
                  (r'\\sum\^\{(.*?)\}',(0,))]:
      try:
         match = re.search(p, string)
         _ = match.groups()
         for ii in range(len(inds)):
            i = inds[ii]
            sumation[i] = match.groups()[ii]
         break
      except: pass
   text = f'sumation'
   if len(sumation[1])>0: text += f' from {sumation[1]}'
   if len(sumation[0])>0: text += f' to {sumation[0]}'
   return f' {text} '


def clean_inline_math(tag):
   """
   substitutes all the <math> tags by its "tex" attribute.
   """
   for math in tag.find_all('math'):
      tex = math.get('tex')
      math.replaceWith(clean_tex(tex))
   return tag


def read_tex(xml_file):
   xml = open(xml_file,'r').read()
   S = BeautifulSoup(xml,'lxml')
   text = 'Title: '+S.find('title').text
   for tag in S.find_all(['p','equation','caption']):
      #XXX Clean ###########
      ## remove citations
      for cite in tag.find_all('cite'):
         cite.replaceWith('')
      ######################
      if tag.name == 'p': text += clean_paragraph(tag)
      elif tag.name == 'equation': text += clean_equation(tag)
      elif tag.name == 'caption': text += clean_caption(tag)
   return text

