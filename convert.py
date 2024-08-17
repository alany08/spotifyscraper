import os

def convert(i="", o="", bitrate=256000):
	ffmpeg.input(i).output(o, ab=str(bitrate), map_metadata=0, id3v2_version=3).run()
	os.remove(i)