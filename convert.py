import os
import ffmpeg
import threading
from config import config
import time
import metadata

_processed_count = 0

def convert(i="", o="", bitrate=256000, total=-1):
	global _processed_count
	t = threading.Thread(target=_convert, kwargs={"i": i, "o": o, "bitrate": bitrate})
	while threading.active_count() > config["thread_cap"] and config["thread_cap"] != 0:
		print(f"Active threads: {threading.active_count() - 1} Processed: {_processed_count}/{total}", end=f"{' '*50}\r", flush=True)
		time.sleep(0.01)
	t.start()

def _convert(i="", o="", bitrate=256000):
	global _processed_count
	song_data = metadata.get_metadata(i)
	ffmpeg.input(i).output(o, ab=str(bitrate), map_metadata=0, id3v2_version=3, loglevel="quiet").run()
	os.remove(i)
	metadata.write_metadata(o, song_data)
	_processed_count += 1