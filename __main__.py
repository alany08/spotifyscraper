from metadata import write_metadata
from spotify import search_for_track

track = search_for_track(name="La vaguelette Instrumental", artist="hoyo-mix")
write_metadata("/home/alan/Downloads/HOYO-MiX - La vaguelette.mp3", track)