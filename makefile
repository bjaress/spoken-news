.PHONY: today
TODAY:=$(shell date --iso)
.PRECIOUS: $(TODAY).raw.txt

today: $(TODAY).artificialnews.mp3

%.raw.txt :
	anews/content.py > $@

%.segmented.txt : %.raw.txt
	anews/sentences.py < $^ > $@

%.m3u : %.segmented.txt
	./text2m3u.hs < $^ > $@

%.artificialnews.mp3 : %.m3u clips/pause.wav
	sox -v 0.7 $< -t wav - rate -v 44100 | lame \
		--add-id3v2 \
		--tt "$(TODAY)" \
		--ta "Artificial News" \
		--tc "bjaress.com/news" \
		- $@


clips/pause.wav : clips/pause.seconds
	sox -n -r 48000 $@ trim 0.0 `cat $^`
