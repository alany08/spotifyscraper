from metadata import write_metadata
from spotify import search_for_track

track = search_for_track(isrc="DGA0L2373345")
write_metadata("/home/alan/Downloads/HOYO-MiX - La vaguelette.mp3", track)