import array
import copy
import getopt
import sys

__author__ = 'Haltux'

import textMatcher
from pysrt import SubRipFile
import pysrt
import matplotlib.pyplot as pyplot

MINIMUM_INTERVAL_GRADIENT_COMPUTATION=60000
MAXIMUM_INTERVAL_GRADIENT_COMPUTATION=300000
SMALL_GRADIENT_DIFF=500
MAX_GRADIENT=0.1
MINIMUM_NB_MATCH=10
SMALL_GRADIENT_INDEX_THRESHOLD=10


def window(x,mini,maxi):
    return min(max(x,mini),maxi)



def get_candidates(tm,subs1,subs2,time_max_shift=pysrt.SubRipTime(minutes=2)):
    candidates=[]
    for sub1 in subs1:
        selected_subs2=subs2.slice(starts_after=sub1.start-time_max_shift,starts_before=sub1.start+time_max_shift)
        for sub2 in selected_subs2:
            if tm.is_similar(sub1.text,sub2.text):
                candidates+=[(sub1,sub2)]
    return candidates

def compute_coefs(times,diffs,x1,x2):
    gradient=float(diffs[x2]-diffs[x1])/float(times[x2]-times[x1])
    v0=diffs[x1]-times[x1]*gradient
    return (v0,gradient)

def get_average_main_cluster(elts,cluster_size):
    clusters=[]

    for (gradient,length) in elts:
        found=False
        for cluster in clusters:
            if abs((gradient-cluster[1])*length)<cluster_size:
                cluster[0].append(gradient)
                cluster[1]=float(sum(cluster[0]))/len(cluster[0])
                found=True
                break
        if not found:
            clusters.append([[gradient],float(gradient)])
    biggest_cluster=max(clusters,key=lambda c:len(c[0]))
    return biggest_cluster[1]

    


def compute_regression(candidates):
    times1=[s1.start.ordinal for (s1,s2) in candidates]
    times2=[s2.start.ordinal for (s1,s2) in candidates]
    diffs=[y-x for (x,y) in zip(times1,times2)]

    l=len(times1)
    lines=[]
    for x1 in range(0,l):
        x2=x1+1
        while x2<len(times1) and times1[x2]-times1[x1]<MINIMUM_INTERVAL_GRADIENT_COMPUTATION:
            x2+=1
        while x2<len(times1) and times1[x2]-times1[x1]<MAXIMUM_INTERVAL_GRADIENT_COMPUTATION:
            v0,gradient=compute_coefs(times1,diffs,x1,x2)
            if abs(gradient)<MAX_GRADIENT:
                lines+=[(v0,gradient,x2-x1)]
            x2+=1


    central_gradient=get_average_main_cluster([(gradient,length) for (v0,gradient,length) in lines],SMALL_GRADIENT_DIFF)

    ratio=1/(1+central_gradient)

    ctimes2=[]
    cdiffs=[]
    cv0s=[]
    for x in range(0,len(diffs)):
        nb_match=0
        for y in range(max(0,x-10),max(0,x-1))+range(min(len(diffs),x+1),min(len(diffs),x+10)):
            shift=diffs[y]-(diffs[x]+(times1[y]-times1[x])*central_gradient)
            if abs(shift)<500:
                nb_match+=1
        if (nb_match>=3): # and abs(shift2)<500):
            ctimes2.append(times2[x])
            cdiffs.append(diffs[x])
            cv0s.append(diffs[x]-times2[x]*central_gradient)



    ax = pyplot.gca()
    ax.set_autoscale_on(False)
    pyplot.axis([min(times1),max(times1),min(cv0s)-10000,max(cv0s)+10000])
    pyplot.plot(times2,diffs,'o')
    pyplot.plot(ctimes2,cdiffs,'go')

    pyplot.plot(times2,[x*central_gradient+cv0s[0] for x in times2],'r-')
    pyplot.show()

    return (ratio,ctimes2,cv0s)

    #A = numpy.vstack([subs1_starts, numpy.ones(len(subs1_starts))]).T
    #m,c=numpy.linalg.lstsq(A,diffs)[0]

def synchronize_subtitles(subtitle,ratio,times,v0s):
    for i in range(0,len(times)):
        if i==0:
            starts_after=0
            shift=-v0s[i]
        else:
            starts_after=times[i-1]
            shift=max(-v0s[i],-v0s[i-1])

        starts_before=times[i]+1



        slice=copy.deepcopy(subtitle.slice(starts_before=starts_before,starts_after=starts_after))
        slice.shift(milliseconds=shift,ratio=ratio)

        if i==0:
            new_subtitle=slice
        else:
            new_subtitle=new_subtitle+slice

    return new_subtitle





def usage():
    print "Usage: ./srtmerge [options] lang1.srt lang2.srt out.srt"
    print "  -e <encoding>             Encoding of input and output files."
    print "  --encoding=<encoding>     default: utf_8"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hd:e:', ["help", "encoding_text_file=", "encoding_time_file=", "encoding_output="])
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

    for o, a in opts:
        if o in ("-e", "--encoding_text_file"):
            encoding1 = a
        elif o in ("--encoding_time_file"):
            encoding2 = a
        elif o in ("--encoding_output_file"):
            encoding_output = a
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

    tm=textMatcher.BilingualTextMatcher()

    candidates= get_candidates(tm,subs_time,subs_text)

    ratio,times,v0s=compute_regression(candidates)

    new_subtitle=synchronize_subtitles(subs_text,ratio,times,v0s)

    if (encoding_output!=""):
        new_subtitle.save(args[2],encoding=encoding_output)
    else:
        new_subtitle.save(args[2])

if __name__ == "__main__":
    main()