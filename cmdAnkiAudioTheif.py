from pydub import AudioSegment
from ankipandas import Collection
from pydub import AudioSegment
import random
import shutil
import os

path = "C:\\Users\\themi\\AppData\\Roaming\\Anki2\\User 1\\collection.media\\"

def check_output_folder():
	if not os.path.isdir("output"):
		os.makedirs("output")

#Combines all audio files in the file_list with the option by default to randomize the list
def concat(file_list,is_random=True):
	audio = AudioSegment.empty()

	if is_random:
		random.shuffle(file_list)

	for file in file_list:
		print("Adding " + file + " to audio...")
		format = ""
		if "mp3" in file:
			format = "mp3"
		else:
			format = "ogg"
		
		sound = AudioSegment.from_file(path + file,format=format);
		audio = audio + sound
	check_output_folder()
	audio.export(out_f = "condensed_audio.wav", format = "wav")

def copy_files(file_list,out_path):
	check_output_folder()
	for file in file_list:
		src = path + file
		dst = out_path +"\\" + file
		if os.path.exists(dst):
			print(file + " aleady exists in output!")
		else:
			print("Copying " + file + " to output...")
			shutil.copy(src, dst)

def audio_file_names(deck_name,note_model):
	col = Collection("C:\\Users\\themi\\AppData\\Roaming\\Anki2\\User 1")
	x = col.cards.merge_notes()
	note_list = x[x.cdeck == deck_name][x.ctype == 'learning'][x.nmodel == note_model]['nflds'].tolist()
	note_list = list(map(lambda x: x[3].replace("[sound:","").replace("]",""), note_list))
	return note_list


def steal(deck_name,note_model,is_concat=False,out_path='output'):
	file_list = audio_file_names(deck_name,note_model)
	
	if is_concat:
		print("Concatenating Audio...")
		concat(file_list)
	else:
		print("Copying files...")
		copy_files(file_list,out_path)
	print("Finished")

deck_name  = "Jlab's beginner course\x1fPart 1: Listening comprehension"
note_model = "JlabNote-JlabConverted-1"
out_path = "E:\\jlab"
steal(deck_name,note_model,out_path=out_path)
