import re

__author__ = 'haltux'


def get_text_length(s):
    return len(s.split)

def removeNonAscii(s):
        return "".join(i for i in s if ord(i)<128)

class BilingualTextMatcher:

    def __init__(self,dictionary_file=""):
        self.dicts=self.get_dictionary_wiktionnaire()



    def get_dictionary_babel(self,dictionary_file="data\\en-fr-babel.txt"):
        f=open(dictionary_file)
        word_counter=0
        dicts=[{},{}]
        for line in f:
            if line[0]!="#":
                line_fields=line.split("\t")
                for i,field in enumerate(line_fields):
                    words=field.split(";")
                    for word in words:
                        dicts[i][word.lower().strip()]=word_counter
                word_counter+=1

        return dicts

    def get_dictionary_wiktionnaire(self,dictionary_file="data\\en-fr-wikt.txt"):
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

        return dicts



    def _preprocess_text(self,t):
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

    def _text_length(self,t):
        return len(self._preprocess_text(t).split(" "))

    def compute_dictionnary_fingerprint(self,sentence,dict_num):
        sentence=self._preprocess_text(sentence)
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
        s0=self._preprocess_text(s0)
        s1=self._preprocess_text(s1)

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
        words0=set(self._preprocess_text(s0).split(" "))
        words1=set(self._preprocess_text(s1).split(" "))
        equal_words=words0.intersection(words1)
        equal_words_not_in_dict=[word for word in equal_words if (not word in self.dicts[0]) and len(word)>2]
        return len(equal_words_not_in_dict)



    def is_similar(self,s0,s1):
        nb_translated_words=self.get_nb_translated_words(s0,s1)
        nb_equal_words=self.get_nb_equal_words(s0,s1)

        nb_matching_words=nb_translated_words+nb_equal_words

        max_text_length=max(self._text_length(s0),self._text_length(s1))
        if nb_matching_words>=(max_text_length/3+1):
            return True
        else:
            return False




