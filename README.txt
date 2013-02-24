SmartSRTSynchronizer

Automatic subtitles synchronizer.

Generates a properly synchronized subtitle file from an out-of-sync subtitle file and a properly synchronized subtitle file in another language. 

Multiplicative and additive factors are supported, as well as gaps in subtitle (changes in the additive factor during the video, often occuring between TV and DVD versions of subtitles).

Usage: ./smartSRTSynchronizer [options] text_file.srt sync_file.srt out.srt"
      -e <encoding>                          Encoding of input text file"
      --encoding_text_file=<encoding>        default: utf_8"
      --encoding_sync_file=<encoding>        default: utf_8"
      --encoding_output=<encoding>           default: utf_8"
      --dictionnary=<dictionnary_file>       default: english-french"
      -g                                     Display output graph (for debugging purposes)"