import spacy
import re
import pandas as pd
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from spacy.matcher import Matcher
from io import StringIO

#Load pretrained model
nlp = spacy.load('en_core_web_sm')

##########

import string

class Resume():
    
    def __init__(self,filename):
        self.filepath = filename
        self.load()
        self.parse()

    def load(self):
        text = ''
        for page in extract_text_from_pdf(self.filepath):
            text += ' ' + page
        self.content = text
        
        
    def checkLine(self,word,value, content, line):
        if word in content.lower():
            value = self.addValue(value,line)
        return value

    def addValue(self,value,line):
        value[line] = value.get(line,0) + 1
        return value

    def dict_List(self,dict_, content):
        new = [(key,value) for key,value in dict_.items() if dict_[key] == max(dict_.values())]
        return [(x[0],content[x[0]]) for x in sorted(new)]

    def get_name(self):
        names = []
        for each in self.name:
            if each[0] not in self.headings:
                each = each[1].replace('Name',"")
                if each[0] not in string.letters:
                    each = each[1:]
                names.append(each.strip())
            else:
                index = self.headings[self.headings.index(each[0])+1]
                names.append("\n".join(self.content[each[0]+1:index]))
        if len(names) == 1:
            return names[0]
        else:
            return names

    def get_work(self):
        experience = []
        for each in self.work:
            index = self.headings[self.headings.index(each[0])+1]
            experience.append("\n".join(self.content[each[0]+1:index]))
        if len(experience) == 1:
            return experience[0]
        else:
            return experience

    def parse(self):
        name = dict()
        work_experience = dict()
        isHeading = dict()
        for line_num in range(len(self.content)):
            for checkName in ["name",":"]:
                name.update(self.checkLine(checkName,name,self.content[line_num], line_num))
            for checkWork in ["work","experience"]:
                work_experience.update(self.checkLine(checkWork,work_experience, self.content[line_num],line_num))
            if line_num != len(self.content) - 1:
                if len(self.content[line_num + 1]) > len(self.content[line_num]):
                    isHeading.update(self.addValue(isHeading,line_num))
            if line_num > 0:
                if self.content[line_num - 1] == "":
                    isHeading.update(self.addValue(isHeading,line_num))
            if len(self.content[line_num]) == len(self.content[line_num].lstrip()):
                isHeading.update(self.addValue(isHeading,line_num))
            if self.content[line_num] == "":
                isHeading[line_num] = isHeading.get(line_num,0) - 1

        self.name = self.dict_List(name, self.content)
        self.work = self.dict_List(work_experience, self.content)
        self.headings = self.dict_List(isHeading, self.content)
        self.headings = [x[0] for x in self.headings]

#########




###Function to extract text from pdf
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()
            
            # create a file handle
            fake_file_handle = StringIO()
            
            # creating a text converter object
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )
             # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )

            # process current page
            page_interpreter.process_page(page)
            
            # extract text
            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()
##############################################



            


###Function to extract name from text //USELESS
def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # initialize matcher with a vocab
    matcher = Matcher(nlp.vocab)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', None, pattern)
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text
###############################################
"""

import nltk
from nameparser.parser import HumanName

def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.node == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)
"""

###Function to extract mobile number //USELESS
def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
##########################################




###Function to extract email //USELESS
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None
##########################################



        

###Function to extract skills //IMPORTANT
def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks

    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # reading the csv file
    data = pd.read_csv("skills.csv") 
    
    # extract values
    skills = list(data.columns.values)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]
###############################################


def extract_file_from_pdf(filename):
    text = ''
    for page in extract_text_from_pdf(filename):
        text += ' ' + page
    return text
'''    
print("Name: " + extract_name(text))
print("Mob.: " + extract_mobile_number(text))
print("email: " + extract_email(text))
print(extract_skills(text))

resume = Resume(filename = 'ronu.pdf' )
print(resume.get_name())
print(resume.get_work())
'''
