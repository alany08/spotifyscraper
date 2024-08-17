import os
import ffmpeg
import threading
from config import config
import sys

_processed_count = 0

def convert(i="", o="", bitrate=256000):
	global _processed_count
	t = threading.Thread(target=_convert, kwargs={"i": i, "o": o, "bitrate": bitrate})
	while threading.active_count() > config["thread_cap"] and config["thread_cap"] != 0:
		sys.stdout.write(f"\rActive threads: {threading.active_count()} Processed: {_processed_count}")
		sys.stdout.flush()
	t.start()

def _convert(i="", o="", bitrate=256000):
	global _processed_count
	sys.stdout.write(f"\rConverting {i}\n")
	sys.stdout.flush()
	ffmpeg.input(i).output(o, ab=str(bitrate), map_metadata=0, id3v2_version=3, loglevel="quiet").run()
	os.remove(i)
	sys.stdout.write(f"\rDone converting {i}\n")
	sys.stdout.flush()
	_processed_count += 1