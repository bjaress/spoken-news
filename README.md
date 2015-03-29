# artificial-news

## Voice

Finally found a voice that doesn't sound threatening, but it only reads
one line then stops.  It also doesn't pause between sentences, which
makes the speech sound relentless and overwhelming.

Current plan is to rearrange the text to have one sentence per line,
then feed the lines in separately, and concatenate the separate output
files with small pauses in between.

Also put a longer pause at paragraph breaks, and maybe some sort of
short music at file/section breaks.

The other problem is that, to me, tho voice sounds a bit fast.
Slowing it down with sox makes it much nicer.

    play tmp.wav speed 0.90 vol 3


## Source Material

* [Wikipedia Headlines][] and the lead
  section of the page behind each bold link.
* Lead section of an article when it stops being listed as an "ongoing
  story."

[Wikipedia Headlines]:
    http://en.wikipedia.org/wiki/Portal:Current_events/Headlines

It will have to keep track of which articles it's seen links to, both
for detecting that something has stopped being an ongoing story and for
avoiding repeats.  A full database seems unnecessary.  It can probably
use two flat files of one URL per line: one for articles that were
listed as ongoing in the previous run, one for the last N articles used.


## Text Processing

## Reformat

One sentence per line, keeping blank lines between paragraphs.

Idea (a slight refinement of Wikipedia's [suggested
approach][sentences]):

Periods, question marks, and exclamation points end sentences unless the
next word is not capitalized or the word in front of the punctuation is
both capitalized and in a pre-compiled set of abbreviations.


## Strip

For now, just take out anything anything outside the main text and
anything in parentheses or square brackets.  Maybe something more
sophisticated later.

[sentences]: http://en.wikipedia.org/wiki/Sentence_boundary_disambiguation#Strategies




## Conversion to MP3

Concatenate the `.wav` files, convert to MP3, and tag.
