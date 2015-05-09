.PHONY: today
TODAY:=$(shell date --iso)
.PRECIOUS: $(TODAY).raw.txt

today: $(TODAY).artificialnews.mp3

%.raw.txt :
	anews/content.py > $@

%.segmented.txt : %.raw.txt
	# Strip out footnotes that are sometimes left in,
	# then segment into sentences.
	grep -v '^\^' $^ | anews/sentences.py > $@

%.m3u : %.segmented.txt
	./text2m3u.hs < $^ > $@

%.artificialnews.mp3 : %.m3u clips/pause.wav
	sox -v 0.7 $< -t wav - rate -v 44100 | lame \
		-b 128 -q 2 \
		--tt "Artificial News $(TODAY)" \
		--ta "bjaress.com/news" \
		- $@


clips/pause.wav : clips/pause.seconds
	sox -n -r 48000 $@ trim 0.0 `cat $^`
