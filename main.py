import array
import copy
import getopt
import sys

__author__ = 'Haltux'

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


def get_candidates(tm,subs1,subs2,time_max_shift=pysrt.SubRipTime(minutes=2)):
    candidates=[]
    for x1,sub1 in enumerate(subs1):
        for x2,sub2 in enumerate(subs2):
            if sub2.start>sub1.start-time_max_shift and sub2.start<sub1.start+time_max_shift:
                if tm.is_similar(sub1.text,sub2.text):
                    candidates+=[Candidate(subs1,subs2,x1,x2)]
    return candidates

def compute_coefs(times,diffs,x1,x2):
    gradient=float(diffs[x2]-diffs[x1])/float(times[x2]-times[x1])
    v0=diffs[x1]-times[x1]*gradient
    return (v0,gradient)

    
def get_main_gradient(candidates):
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

def filter_outliers(candidates,gradient):
    filtered_candidates=[]
    for x in range(0,len(candidates)):
            nb_match=0
            for y in range(max(0,x-10),max(0,x-1))+range(min(len(candidates),x+1),min(len(candidates),x+10)):
                shift=candidates[y].diff()-(candidates[x].diff()+(candidates[y].time2()-candidates[x].time2())*gradient)
                if abs(shift)<SMALL_TIME_DIFF:
                    nb_match+=1
            if (nb_match>=3): # and abs(shift2)<500):
                filtered_candidates.append(candidates[x])
    return filtered_candidates


def compute_regression(candidates,display_graph):
    gradient=get_main_gradient(candidates)

    filtered_candidates=filter_outliers(candidates,gradient)

    if (display_graph):
        import matplotlib.pyplot as pyplot
        ax = pyplot.gca()
        ax.set_autoscale_on(False)
        times2=[c.time2() for c in candidates]
        cv0s=[c.v0(gradient) for c in filtered_candidates]
        pyplot.axis([min(times2),max(times2),min(cv0s)-10000,max(cv0s)+10000])
        pyplot.plot([c.time2() for c in candidates],[c.diff() for c in candidates],'o')
        pyplot.plot([c.time2() for c in filtered_candidates],[c.diff() for c in filtered_candidates],'go')

        pyplot.plot(times2,[x*gradient+filtered_candidates[0].v0(gradient) for x in times2],'r-')
        pyplot.show()

    return (gradient,candidates)


def synchronize_subtitles(subtitle,gradient,matchs):
    for i in range(0,len(matchs)):
        if i==0:
            starts_after=0
            shift=-matchs[i].v0(gradient)
        else:
            starts_after=matchs[i-1].time2()
            shift=max(-matchs[i].v0(gradient),-matchs[i-1].v0(gradient))

        starts_before=matchs[i-1].time2()+1



        slice=copy.deepcopy(subtitle.slice(starts_before=starts_before,starts_after=starts_after))
        slice.shift(milliseconds=shift,ratio=1/(1+gradient))

        if i==0:
            new_subtitle=slice
        else:
            new_subtitle=new_subtitle+slice

    return new_subtitle





def usage():
    print "Usage: ./smartSRTSynchronizer [options] text_file.srt sync_file.srt out.srt"
    print "  -e <encoding>                          Encoding of input text file"
    print "  --encoding_text_file=<encoding>        default: utf_8"
    print "  --encoding_sync_file=<encoding>        default: utf_8"
    print "  --encoding_output=<encoding>           default: utf_8"
    print "  --dictionnary=<dictionnary_file>       default: english-french"
    print "  -g                                     Display output graph (for debugging purposes)"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hgd:e:', ["help", "encoding_text_file=", "encoding_time_file=", "encoding_output=","dictionnary="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    if len(args) <> 3:
        usage()
        sys.exit(2)

    encoding1=""
    encoding2=""
    encoding_output=""
    dictionary_file=""
    display_graph=False

    for o, a in opts:
        if o in ("-e", "--encoding_text_file"):
            encoding1 = a
        elif o in ("--encoding_time_file"):
            encoding2 = a
        elif o in ("--encoding_output_file"):
            encoding_output = a
        elif o in ("--dictionary"):
            dictionary_file = a
        elif o in ("-g"):
            display_graph=True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()



    if (encoding1!=""):
        subs_text = SubRipFile.open(args[0], encoding=encoding1)
    else:
        subs_text = SubRipFile.open(args[0])

    if (encoding2!=""):
        subs_time = SubRipFile.open(args[1], encoding=encoding2)
    else:
        subs_time = SubRipFile.open(args[1])

    if (dictionary_file==""):
        tm=textMatcher.BilingualTextMatcher()
    else:
        tm=textMatcher.BilingualTextMatcher(dictionary_file)

    candidates= get_candidates(tm,subs_time,subs_text)

    gradient,matchs=compute_regression(candidates,display_graph)
    
    new_subtitle=synchronize_subtitles(subs_text,gradient,matchs)

    if (encoding_output!=""):
        new_subtitle.save(args[2],encoding=encoding_output)
    else:
        new_subtitle.save(args[2])

if __name__ == "__main__":
    main()