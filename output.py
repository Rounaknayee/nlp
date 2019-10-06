from be import *

document = extract_file_from_pdf('ronu.pdf')

#print(document)

import nltk
from nltk.corpus import stopwords
stop = stopwords.words('english')
document = ''.join([i for i in document.split() if i not in stop])
sentences = nltk.sent_tokenize(document)
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]
print(sentences)
