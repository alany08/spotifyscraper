import os
import ffmpeg
import threading
from config import config

_processed_count = 0

def convert(i="", o="", bitrate=256000):
	global _processed_count
	t = threading.Thread(target=_convert, kwargs={"i": i, "o": o, "bitrate": bitrate}, daemon=True)
	while threading.active_count() > config["thread_cap"] and config["thread_cap"] != 0:
		pass
	t.start()

def _convert(i="", o="", bitrate=256000):
	global _processed_count
	ffmpeg.input(i).output(o, ab=str(bitrate), map_metadata=0, id3v2_version=3, loglevel="quiet").run()
	os.remove(i)
	_processed_count += 1