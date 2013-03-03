import os
import re
import sys

__author__ = 'haltux'

REQUIRED_MATCH_RATIO=3

def removeNonAscii(s):
    return "".join(i for i in s if ord(i)<128)


def preprocess_text(t):
    output_string=removeNonAscii(t)\
        .replace(","," ")\
        .replace("\n"," ")\
        .replace("."," ")\
        .replace(";"," ")\
        .replace("'","' ")\
        .replace("?"," ")\
        .replace("!"," ")\
        .replace("  "," ")\
        .replace("  "," ")\
        .strip().lower()
    output_string=re.sub("\{[^\{]*\}","",output_string)
    output_string=re.sub("<[^<]*>","",output_string)
    return output_string


def nb_words(t):
    return len(preprocess_text(t).split(" "))



class BilingualTextMatcher:

    def __init__(self,dictionary_file="",invert_dictionary=False):
        if dictionary_file!="":
            self.get_dictionary_wiktionary()
        else:
            self.get_dictionary_wiktionary(dictionary_file,invert_dictionary)



    def get_dictionary_wiktionary(self,dictionary_file="",invert_dictionary=False):
        if (dictionary_file==""):
            import pkgutil
            import StringIO
            f=StringIO.StringIO(pkgutil.get_data(__name__,"data/en-fr-wikt.txt"));
        else:
            f=open(dictionary_file)
        dicts=[{},{}]

        for line in f:
            if line[0]!="#":
                line_fields=line.split("\t")

                pp_words_0=[re.sub("\([^\(]*\)","",removeNonAscii(word)).lower().strip() for word in line_fields[0].split(",")]
                pp_words_1=[re.sub("\([^\(]*\)","",removeNonAscii(word)).lower().strip() for word in line_fields[1].split(",")]

                for word0 in pp_words_0:
                    for word1 in pp_words_1:
                        if word0 in dicts[0]:
                            dicts[0][word0]+=[word1]
                        else:
                            dicts[0][word0]=[word1]
                        if word1 in dicts[1]:
                            dicts[1][word1]+=[word0]
                        else:
                            dicts[1][word0]=[word0]
        
        if invert_dictionary:
            self.dicts=[dicts[1],dicts[0]]
        else:
            self.dicts=dicts



    def compute_dictionnary_fingerprint(self,sentence,dict_num):
        sentence=preprocess_text(sentence)
        words=sentence.split(" ")
        fingerprint=set()
        for i,word in enumerate(words):
            for l_seq in range(4,0,-1):
                if i+l_seq<=len(words):
                    seq=" ".join(words[i:i+l_seq])
                    if seq in self.dicts[dict_num]:
                        fingerprint.add(self.dicts[dict_num][seq])

        return fingerprint

    def get_nb_translated_words(self,s0,s1):
        s0=preprocess_text(s0)
        s1=preprocess_text(s1)

        words0=s0.split(" ")
        words1=s1.split(" ")

        nb_match=0
        for word0 in words0:
            if word0 in self.dicts[0]:
                for word1 in words1:
                    if word1 in self.dicts[0][word0]:
                        nb_match+=1
        return nb_match
                    

    def get_nb_equal_words(self,s0,s1):
        words0=set(preprocess_text(s0).split(" "))
        words1=set(preprocess_text(s1).split(" "))
        equal_words=words0.intersection(words1)
        equal_words_not_in_dict=[word for word in equal_words if (not word in self.dicts[0]) and len(word)>2]
        return len(equal_words_not_in_dict)



    def is_similar(self,s0,s1):
        nb_translated_words=self.get_nb_translated_words(s0,s1)
        nb_equal_words=self.get_nb_equal_words(s0,s1)

        nb_matching_words=nb_translated_words+nb_equal_words

        max_text_length=max(nb_words(s0),nb_words(s1))
        if nb_matching_words>=(max_text_length/REQUIRED_MATCH_RATIO+1):
            return True
        else:
            return False




