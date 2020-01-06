#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from urllib.request import Request, urlopen, urlretrieve
import text
import datetime as dt
from bs4 import BeautifulSoup
import os
import console
## LOG
import logging
LG = logging.getLogger(__name__)



class Author(object):
   def __init__(self,name='',href=''):
      self.name = name
      self.url = href
   def __str__(self):
      msg = self.name + '\n'
      if len(self.url) > 0: msg += self.url + '\n'
      return msg

class ArXivEntry(object):
   def __init__(self,title='', authors=[], abstract='', subject=[], ID='',\
                     urlabs='', urlpdf='', index=None):
      #self.title = '\033[1m' + title + '\033[0m'
      self.title = title
      self.author = authors
      self.abstract = abstract
      self.subjects = subject
      self.ID = ID
      self.urlabs = urlabs
      self.urlpdf = urlpdf
      self.index = index
   def __str__(self):
      #msg = '\033[1m' + text.center('%s\n'%(self.title)) + '\033[0m'
      msg = ''
      if self.index != None: msg += '[%s] '%(self.index)
      msg +=  'arXivID: %s\n'%(self.ID)
      msg += text.title(self.title)
      msg += 'Author'
      if len(self.author) > 1: msg += 's: '
      else: msg += ': '
      msg += ', '.join([a.name for a in self.author]) + '\n'
      msg += self.abstract+'\n'
      if len(self.subjects)>0: msg+='subjects: '+' '.join(self.subjects) + '\n'
      msg += 'pdf: %s'%(self.urlpdf)
      return msg
   def clean_abstract(self):
      """ remove symbols etc """
      stop_words = set(stopwords.words('english'))
      self.abs = self.abstract.lower()
      for s in ['(',')',',','.','-','[',']','{','}']:
         self.abs = self.abs.replace(s,' ')
      filtered = [w for w in self.abs.split() if w not in stop_words]
      self.abs = ' '.join(filtered)
      return self.abs

def make_request(url):
   """ Make http request """
   req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   html_doc = urlopen(req)
   html_doc = html_doc.read().decode(html_doc.headers.get_content_charset())
   return html_doc

def get_paper_info(url):
   """
   Process an arxiv entry and returns an ArxivEntry class
   Assumes url structure:  https://arxiv.org/abs/arXiv.id
   """
   if url[-1] == '/': url = url[:-1]
   arXiv_id = url.split('/')[-1]
   urlpdf = url.replace('/abs/','/pdf/')
   html_doc = make_request(url)
   S = BeautifulSoup(html_doc, 'html.parser')
   title = S.find('h1',class_='title mathjax').text.replace('Title:\n','')
   title = ' '.join( title.lstrip().rstrip().split() )
   for x in S.find_all('div', class_='authors'):
      x = x.text.replace('Authors:\n','')
      authors = []
      for author in x.split('\n'):
         auth = author.replace(',','').split()
         author = ' '.join(auth)
         authors.append(author)
   txt = S.find('blockquote', class_='abstract mathjax').text.lstrip().rstrip()
   txt = txt.replace('Abstract: ','')
   abstract = text.clean( txt )
   subjects = [s.text for s in S.find_all('span', class_='primary-subject') ]
   return ArXivEntry(title,authors,abstract,subjects,arXiv_id,urlpdf)


def parse_arxiv(fname,URLbase='https://arxiv.org'):
   """ Parse the html code from an arxiv "new" section """
   today = dt.datetime.now().date()
   html_doc = open(fname,'r').read()
   S = BeautifulSoup(html_doc, 'html.parser')
   h3 = S.find('h3').text
   date = h3.split('for')[-1].lstrip().rstrip()
   date = dt.datetime.strptime(date,'%a, %d %b %y').date()

   NewSub = []
   CrossList = []
   Replacements = []
   sections = [NewSub, CrossList, Replacements]
   titles = []
   sect = 0
   for dl,h3 in zip(S.find_all('dl'),S.find_all('h3')):
      ## Skip replacements
      section = h3.text.split('for')[0].lstrip().rstrip() 
      if section not in ['New submissions', 'Cross-lists']: continue
      ## report section.  #TODO log this
      # h = '** ' + h3.text + ' *'
      # while len(h) < console.getTerminalSize()[0]:
      #    h += '*'
      h = h3.text
      titles.append(h)
      for dt_tag,dd_tag in zip(dl.find_all('dt'), dl.find_all('dd')):
         ## parsing dt tag
         index = int(dt_tag.find('a').text.replace('[','').replace(']',''))
         arxivID = dt_tag.find('a',title='Abstract').text.replace('arXiv:','')
         URLabs = URLbase + dt_tag.find('a',title='Abstract')['href']
         URLpdf = URLbase + dt_tag.find('a',title='Download PDF')['href']
         ## parsing dd tag
         # Title
         title = dd_tag.find('div',class_='list-title mathjax').text
         title = text.clean(title.replace('Title: ',''))
         # Authors
         authors = []
         for auth in dd_tag.find('div',class_='list-authors').find_all('a'):
            authors.append( Author(auth.text,URLbase+auth['href']) )
         # Subjects
         subjects = dd_tag.find('div',class_='list-subjects').text
         subjects = subjects.replace('Subjects: ','').split(';')
         subjects = [x.lstrip().rstrip() for x in subjects]
         # Abstract
         abstract = text.clean(dd_tag.find('p', class_='mathjax').text)
         ## arXiv entry
         A = ArXivEntry(title=title, authors=authors, abstract=abstract,
                         subject=subjects, ID=arxivID, urlabs=URLabs,
                         urlpdf=URLpdf, index=index)
         sections[sect].append(A)
      sect += 1
   return titles,sections

def download_paper(ID,fol='.'):
   """ Download the source code of the paper """
   LG.info(f'Downloading from https://arxiv.org/e-print/{ID}')
   #TODO download also the pdf: https://arxiv.org/pdf/{ID}.pdf
   stat = urlretrieve(f'https://arxiv.org/e-print/{ID}',f'/tmp/{ID}')
   ext = stat[1]['Content-Type'].replace('application/','')
   types = {'x-eprint-tar':'tar.gz', 'pdf':'pdf'}
   ext = types[ext]
   com = f'mv /tmp/{ID} {fol}/{ID}.{ext}'
   os.system(com)
   if ext == 'tar.gz':
      com = f'mkdir -p {fol}/{ID}'
      LG.debug(com)
      os.system(com)
      com = f'tar -C {fol}/{ID}/ -xzvf {fol}/{ID}.tar.gz'
      LG.debug(com)
      os.system(com)
      com = f'rm {fol}/{ID}.tar.gz'
      LG.debug(com)
      os.system(com)
   elif ext == 'pdf':
      pass
   LG.info(f'{ID} downloaded')


if __name__ == '__main__':
   import tts
   import config
   import text
   import os
   import datetime as dt
   here = os.path.dirname(os.path.realpath(__file__))  # script folder
   today = dt.datetime.now().date()

   import logging
   logging.basicConfig(level=logging.DEBUG,
                     format='%(asctime)s-%(name)-s-%(levelname)-s-%(message)s',
                     datefmt='%Y/%m/%d-%H:%M',
                     filename=here+'/arxiver.log', filemode='a')
   sh = logging.StreamHandler()
   sh.setLevel(logging.WARNING)
   fmt = logging.Formatter('%(name)s: %(levelname)s %(message)s')
   sh.setFormatter(fmt)
   logging.getLogger('').addHandler(sh)
   LG = logging.getLogger('main')

   
   S = tts.Speaker()
   S.say('Downloading New Submissions', 'Downloading New Submissions')
   C = config.load('config.ini')
   print(text.section('Options for arxiv.py'))
   print(C)
   print(text.spacer())
   URLbase = 'https://arxiv.org'
   # fdata = here + '/data/'
   url = f'{URLbase}/list/{C.areas}/new'
   LG.info('Attempting to download '+url)
   html_doc = make_request(url) # Main web site

   # if not os.path.isdir(fdata): os. system(f'mkdir -p {fdata}')
   fname = f'{C.folder_html}/{today.strftime("%y%m.%d")}.arxiv'
   with open(fname,'w') as f:
      f.write(html_doc)
   LG.info('Saved to '+fname)
