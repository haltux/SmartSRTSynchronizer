SmartSRTSynchronizer

Automatic subtitles synchronizer.

Generates a properly synchronized subtitle file from an out-of-sync subtitle file and a properly synchronized subtitle file in another language. 

Multiplicative and additive factors are supported, as well as gaps in subtitle (changes in the additive factor during the video, often occuring between TV and DVD versions of subtitles).

Usage:   ./smartSRTSynchronizer [options] text_file.srt sync_file.srt out.srt
         ./smartSRTSynchronizer [options]
      -e <encoding>                          Encoding of input text file
      --encoding_text_file=<encoding>
      --encoding_sync_file=<encoding>
      --encoding_output=<encoding>
      --dictionary=<dictionary_file>            use external wiktionary dictionnary
                                                default provided dictionary: english-french
      --invert-dictionary                       not inverted mode: target dictionary language = text subtitle language
                                                inverted mode: target dictionary language = sync subtitle language
      --max_shift=X                             maximum shift between subtitles, in min. default:5
      -g                                        Display output graph (for debugging purposes)