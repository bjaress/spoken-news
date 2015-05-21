.PHONY: today
TODAY:=$(shell date --iso)
.PRECIOUS: $(TODAY).raw.txt

today: $(TODAY).artificialnews.mp3

%.raw.txt :
	snews/content.py > $@

%.segmented.txt : resources/intro.raw.txt %.raw.txt resources/closing.raw.txt
	# Add internal date stamp, strip out footnotes that are sometimes
	# left in, then segment into sentences.
	(date --date="$*" "+%A, %-d %B %Y" ; echo) |\
		cat - $^ | grep -v '^\^' | snews/sentences.py > $@

%.m3u : %.segmented.txt
	./text2m3u.hs < $^ > $@

%.artificialnews.mp3 : %.m3u resources/pause.wav
	sox -v 0.7 $< -t wav - rate -v 44100 | lame \
		-b 128 -q 2 \
		--tt "Artificial News $*" \
		--ta "bjaress.com/news" \
		- $@


resources/pause.wav : resources/pause.seconds
	sox -n -r 48000 $@ trim 0.0 `cat $^`
