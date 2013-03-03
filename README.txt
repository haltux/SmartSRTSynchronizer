SmartSRTSynchronizer

Automatic subtitles synchronizer.

Inputs:
- An out-of-sync subtitle file in language A (default french)
- A properly synchronized subtitle file in language B (default english)

Outputs:
- A properly synchronized subtitle file in language A

Multiplicative and additive factors are supported, as well as gaps in subtitles (modification of additive factor during the video), which typically occur with fade to blacks, often added in TV versions.

SmartSRTSynchronizer requires a dictionary. A french-english dictionary is provided and used by default. Other dictionaries has to be provided in the wiktionary format. They can be downloaded from here: http://www.dicts.info/uddl.php


Usage:   ./smartSRTSynchronizer [options] text_file.srt sync_file.srt out.srt
         ./smartSRTSynchronizer [options]
      -e <encoding>                             Encoding of input text file
      --encoding_text_file=<encoding>
      --encoding_sync_file=<encoding>
      --encoding_output=<encoding>
      --dictionary=<dictionary_file>            use external wiktionary dictionnary
                                                default provided dictionary: english-french
      --invert-dictionary       not inverted mode:
                                    target dictionary language = text subtitle language
                                inverted mode:
                                    target dictionary language = sync subtitle language
      --max_shift=X                             maximum shift between subtitles, in min. default:5
      -g                                        Display output graph 