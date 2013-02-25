import array
import copy
import getopt
import sys

__author__ = 'haltux'

import textMatcher
from pysrt import SubRipFile
import pysrt


MINIMUM_INTERVAL_GRADIENT_COMPUTATION=60000
MAXIMUM_INTERVAL_GRADIENT_COMPUTATION=300000
SMALL_TIME_DIFF=500
MAX_GRADIENT=0.1
STEP_GRADIENT=0.001
BIN_SIZE_MS_GRADIENT_COMPUTATION=100
MINIMUM_NB_MATCH=10
SMALL_GRADIENT_INDEX_THRESHOLD=10

SURROUNDING_NB_MATCH_REQUIRED_STEP1=4
SURROUNDING_SIZE_STEP1=5

SURROUNDING_NB_MATCH_REQUIRED_STEP2=4
SURROUNDING_SIZE_STEP2=10


def window(x,mini,maxi):
    return min(max(x,mini),maxi)

class Candidate:
    def __init__(self,subs1,subs2,x1,x2):
        self.subs1=subs1
        self.subs2=subs2
        self.x1=x1
        self.x2=x2

    def diff(self):
        return self.subs2[self.x2].start.ordinal-self.subs1[self.x1].start.ordinal

    def time1(self):
        return self.subs1[self.x1].start.ordinal

    def time2(self):
        return self.subs2[self.x2].start.ordinal
    
    def v0(self,gradient):
        return self.diff()-gradient*self.time2()

    def check_surrounding_subtitles(self):
        surrounding_pairs=[(x1,x2) for x1 in range(max(0,self.x1-SURROUNDING_SIZE_STEP1),self.x1) for x2 in range(max(0,self.x2-SURROUNDING_SIZE_STEP1),self.x2)] +\
                          [(x1,x2) for x1 in range(self.x1+1,min(len(self.subs1),self.x1+SURROUNDING_SIZE_STEP1+1)) for x2 in range(self.x2+1,min(len(self.subs2),self.x2+SURROUNDING_SIZE_STEP1+1))]
        nb_match=0
        for (sx1,sx2) in surrounding_pairs:
            sc=Candidate(self.subs1,self.subs2,sx1,sx2)
            if abs(self.diff()-sc.diff())<SMALL_TIME_DIFF:
                nb_match+=1
        return (nb_match>=SURROUNDING_NB_MATCH_REQUIRED_STEP1)


def generate_candidates_from_text_content(tm,subs1,subs2,time_max_shift=pysrt.SubRipTime(minutes=2)):
    candidates=[]
    for x1,sub1 in enumerate(subs1):
        for x2,sub2 in enumerate(subs2):
            if sub2.start>sub1.start-time_max_shift and sub2.start<sub1.start+time_max_shift:
                if tm.is_similar(sub1.text,sub2.text):
                    candidates+=[Candidate(subs1,subs2,x1,x2)]
    return candidates

def filter_candidates_from_neighbourhood(candidates):
    return [candidate for candidate in candidates if candidate.check_surrounding_subtitles()]
    
def compute_gradient(candidates):
    biggest_bin_best_gradient=0
    best_gradient=0
    gradient=-MAX_GRADIENT
    while gradient<MAX_GRADIENT:
        v0_bins={}
        for candidate in candidates:
            v0=candidate.v0(gradient)
            bin_number=int(v0/BIN_SIZE_MS_GRADIENT_COMPUTATION)
            if bin_number in v0_bins:
                v0_bins[bin_number]+=1
            else:
                v0_bins[bin_number]=1
            if bin_number+1 in v0_bins:
                v0_bins[bin_number+1]+=1
            else:
                v0_bins[bin_number+1]=1
        biggest_bin=max(v0_bins.values())
        if biggest_bin>biggest_bin_best_gradient:
            best_gradient=gradient
            biggest_bin_best_gradient=biggest_bin
        gradient+=STEP_GRADIENT
    return best_gradient

def filter_isolated_candidates(candidates,gradient):
    filtered_candidates=[]
    for x in range(0,len(candidates)):
            nb_match=0
            for y in range(max(0,x-SURROUNDING_SIZE_STEP2),x)+range(min(len(candidates),x+1),min(len(candidates),x+SURROUNDING_SIZE_STEP2)):
                shift=candidates[y].diff()-(candidates[x].diff()+(candidates[y].time2()-candidates[x].time2())*gradient)
                if abs(shift)<SMALL_TIME_DIFF:
                    nb_match+=1
            if (nb_match>=SURROUNDING_NB_MATCH_REQUIRED_STEP2): # and abs(shift2)<500):
                filtered_candidates.append(candidates[x])
    return filtered_candidates



def display_candidates(gradient,candidates1,candidates2,candidates3):
    import matplotlib.pyplot as pyplot
    ax = pyplot.gca()
    ax.set_autoscale_on(False)
    times2=[c.time2() for c in candidates1]
    cv0s=[c.v0(gradient) for c in candidates3]
    pyplot.axis([min(times2),max(times2),min(cv0s)-10000,max(cv0s)+10000])

    pyplot.plot([c.time2() for c in candidates1],[c.diff() for c in candidates1],'o',color="#FFBBBB")
    pyplot.plot([c.time2() for c in candidates2],[c.diff() for c in candidates2],'o',color="#FF8888")
    pyplot.plot([c.time2() for c in candidates3],[c.diff() for c in candidates3],'o',color="#FF0000")


    #pyplot.plot(times2,[x*gradient+matching_candidates[0].v0(gradient) for x in times2],'r-')
    pyplot.draw()


def synchronize_subtitles(subtitle,gradient,matchs):
    for i in range(0,len(matchs)):
        if i==0:
            starts_after=0
            shift=-matchs[i].v0(gradient)
            starts_before=matchs[0].time2()+1
        else:
            starts_after=matchs[i-1].time2()
            starts_before=matchs[i].time2()+1
            shift=max(-matchs[i].v0(gradient),-matchs[i-1].v0(gradient))

        slice=copy.deepcopy(subtitle.slice(starts_before=starts_before,starts_after=starts_after))
        slice.shift(milliseconds=shift,ratio=1/(1+gradient))

        if i==0:
            new_subtitle=slice
        else:
            new_subtitle=new_subtitle+slice

    return new_subtitle





def usage():
    print "Usage:   ./smartSRTSynchronizer [options] text_file.srt sync_file.srt out.srt"
    print "         ./smartSRTSynchronizer [options]"
    print "  -e <encoding>                          Encoding of input text file"
    print "  --encoding_text_file=<encoding>        "
    print "  --encoding_sync_file=<encoding>        "
    print "  --encoding_output=<encoding>           "
    print "  --dictionary=<dictionary_file>       use external wiktionary dictionnary"
    print "                                         default provided dictionary: english-french"
    print "  --invert-dictionary                    no inverted mode: target dictionary language = text subtitle language"
    print "                                         inverted mode: target dictionary language = sync subtitle language"
    print "  -g                                     Display output graph (for debugging purposes)"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hgd:e:', ["help", "encoding_text_file=", "encoding_time_file=", "encoding_output=","dictionary=","invert_dictionary"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    use_gui=False


    if (len(args)==3):
        text_file=args[0]
        sync_file=args[1]
        output_file=args[2]
    elif (len(args)==0):
        use_gui=True
    else:
        usage()
        sys.exit(2)

    encoding1=""
    encoding2=""
    encoding_output=""
    dictionary_file=""
    display_graph=False
    invert_dictionary=False


    for o, a in opts:
        if o in ("-e", "--encoding_text_file"):
            encoding1 = a
        elif o in ("--encoding_time_file"):
            encoding2 = a
        elif o in ("--encoding_output_file"):
            encoding_output = a
        elif o in ("--dictionary"):
            dictionary_file = a
        elif o in ("--invert-dictionary"):
            invert_dictionary=True
        elif o in ("-g"):
            display_graph=True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()


    if use_gui:
        from Tkinter import Tk
        from tkFileDialog import askopenfilename
        from tkFileDialog import asksaveasfilename

        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        text_file = askopenfilename(title="Please choose input SRT file with target subtitle text")
        sync_file = askopenfilename(title="Please choose input SRT file with target subtitle synchronisation")
        output_file=asksaveasfilename(title="Please choose output SRT file")


    if (encoding1!=""):
        subs_text = SubRipFile.open(text_file, encoding=encoding1)
    else:
        subs_text = SubRipFile.open(text_file)

    if (encoding2!=""):
        subs_time = SubRipFile.open(sync_file, encoding=encoding2)
    else:
        subs_time = SubRipFile.open(sync_file)

    if (dictionary_file==""):
        tm=textMatcher.BilingualTextMatcher()
    else:
        tm=textMatcher.BilingualTextMatcher(dictionary_file,invert_dictionary)

    candidates= generate_candidates_from_text_content(tm,subs_time,subs_text)

    print "Number of matches (first pass): ",len(candidates)

    selected_candidates=filter_candidates_from_neighbourhood(candidates)

    print "Number of matches (second pass): ",len(selected_candidates)

    gradient=compute_gradient(candidates)

    matching_candidates=filter_isolated_candidates(selected_candidates,gradient)

    if display_graph:
        display_candidates(gradient,candidates,selected_candidates,matching_candidates)

    print "Number of matches (third pass): ",len(matching_candidates)

    print "Multiplier: ",1/(1+gradient)

    new_subtitle=synchronize_subtitles(subs_text,gradient,matching_candidates)

    if (encoding_output!=""):
        new_subtitle.save(output_file,encoding=encoding_output)
    else:
        new_subtitle.save(output_file)

    print "New subtitle file saved"
    if (display_graph):
        import matplotlib.pyplot as pyplot
        pyplot.show()


if __name__ == "__main__":
    main()