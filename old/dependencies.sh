#! /bin/sh

# http://homepages.inf.ed.ac.uk/jyamagis/software/page54/page54.html

cd `mktemp -d`

wget \
'http://homepages.inf.ed.ac.uk/jyamagis/release/EnglishHTSVoices-ver1.0.tar.gz'

tar xzvf EnglishHTSVoices-ver1.0.tar.gz
cd EnglishHTSVoices

chmod u+x do_build
./do_build

mv build "$OLDPWD"/voices
