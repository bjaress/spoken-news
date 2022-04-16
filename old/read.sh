#! /bin/bash

INFILE="$1"
OUTFILE="$2"

voices/bin/flite_hts_engine \
     -td voices/hts_voice_cstr_uk_female-1.0/tree-dur.inf -tf voices/hts_voice_cstr_uk_female-1.0/tree-lf0.inf -tm voices/hts_voice_cstr_uk_female-1.0/tree-mgc.inf \
     -md voices/hts_voice_cstr_uk_female-1.0/dur.pdf         -mf voices/hts_voice_cstr_uk_female-1.0/lf0.pdf       -mm voices/hts_voice_cstr_uk_female-1.0/mgc.pdf \
     -df voices/hts_voice_cstr_uk_female-1.0/lf0.win1        -df voices/hts_voice_cstr_uk_female-1.0/lf0.win2      -df voices/hts_voice_cstr_uk_female-1.0/lf0.win3 \
     -dm voices/hts_voice_cstr_uk_female-1.0/mgc.win1        -dm voices/hts_voice_cstr_uk_female-1.0/mgc.win2      -dm voices/hts_voice_cstr_uk_female-1.0/mgc.win3 \
     -cf voices/hts_voice_cstr_uk_female-1.0/gv-lf0.pdf      -cm voices/hts_voice_cstr_uk_female-1.0/gv-mgc.pdf    -ef voices/hts_voice_cstr_uk_female-1.0/tree-gv-lf0.inf \
     -em voices/hts_voice_cstr_uk_female-1.0/tree-gv-mgc.inf -k  voices/hts_voice_cstr_uk_female-1.0/gv-switch.inf \
     -s  48000.0\
     -p  300.0\
     -a  0.55\
     -g  0.0\
     -b  -0.8\
     -u  0.5\
     -jm 0.8 \
     -o  "$OUTFILE" \
     "$INFILE"

