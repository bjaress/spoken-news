Plan

Instead of read.sh, have text2m3u.hs that generates a wav file for each
text line, includes a reference to some kind of chime or marker wav for
separator lines, and includes a reference to pause.wav after each line.
(Blank lines should lead to a double reference to puase.wav.)

Sox can take .m3u as input and look up the referenced .wav files, so
just pipe the output of that to lame and include arguments to lame for
the id3 tags.
