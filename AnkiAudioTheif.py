from pydub import AudioSegment
from ankipandas import Collection
from pydub import AudioSegment
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import random
import shutil
import os

# Gets information used to access notes in database
col_path = os.getenv('APPDATA') + "\\Anki2\\User 1"
col_cards = Collection(col_path).cards.merge_notes()
col_notes = Collection(col_path).notes.fields_as_columns(inplace=False)

# Makes output folder if one does not exist
def check_output_folder(out_path):
	if not os.path.isdir(out_path):
		os.makedirs(out_path)

# Deletes "old" files
def delete_stale_output():
	file_type=[".mp3",".ogg",".wav",".flac"]
	out_path = dir_var.get()
	for file in os.listdir(out_path):
		if any(list(map(lambda x: file.endswith(x),file_type))):
			os.remove(out_path+"\\"+file)

# Copies files from the anki media folder and places them into the output folder. 
def copy_files(file_list):
	out_path = dir_var.get()
	check_output_folder(out_path)
	files_copied    = 0
	files_in_output = 0
	files_missing   = 0

	if should_delete_var.get() == 1:
		delete_stale_output()

	for file in file_list:
		src = col_path + "\\collection.media\\" + file
		dst = out_path +"\\" + file
		if not os.path.exists(src):
			files_missing = files_missing + 1
			continue
		if os.path.exists(dst):
			files_in_output = files_in_output + 1
		else:
			shutil.copy(src, dst)
			files_copied = files_copied + 1
	message_string = "Files Found  : " + str(len(file_list) - files_missing) + "/" + str(len(file_list)) + "\n" 
	message_string += "Files Copied : " + str(files_copied) + "\n"
	message_string += "Files Skipped : " + str(files_in_output)
	tk.messagebox.showinfo("Message",message_string)

# Gets a list of every audio file in the card selection 
def get_audio_file_list(deck_name,note_model,field):
	nan_value = float("NaN")
	field = "nfld_" + field
	x = col_cards.merge(col_notes, how='left', left_on='nguid', right_on='nguid')

	note_list = []
	if radio_option.get() == 1:
		note_list = x[x.cdeck == deck_name][x.cqueue != 'new'][x.nmodel_y == note_model][field].tolist()
	elif radio_option.get() == 2:
		note_list = x[x.cdeck == deck_name][x.ctype =='review'][x.nmodel_y == note_model][field].tolist()
	elif radio_option.get() == 3:
		note_list = x[x.cdeck == deck_name][x.nmodel_y == note_model][field].tolist()
	elif radio_option.get() == 4:
		note_list = x[x.cdeck == deck_name][x.cqueue == 'new'][x.nmodel_y == note_model][field].tolist()

	note_list = [x[7:-1] for x in note_list if x.startswith("[sound:")]
	return note_list

# get the list of all decks in the database
def get_deck_list():
	return col_cards.list_decks()
	
# Get the note models that exist in a deck	
def get_deck_models(deck_name):
	note_list = col_cards[col_cards.cdeck == deck_name]['nmodel'].tolist()
	return list(set(note_list))

# Get fields from a note
def get_fields(model_name):
	nan_value = float("NaN")

	c = col_notes[col_notes.nmodel == model_name]
	c = c.replace('', nan_value, inplace=False)
	c = c.dropna(how='all', axis=1, inplace=False)

	field_list = [x[5:] for x in list(c[c.nmodel == model_name]) if x.startswith("nfld_")]
	return field_list

# Set values in combo boxes
def set_combo_box_items(model_combo_box,items):
	model_combo_box['values'] = items
	model_combo_box.current(newindex=0)

# Sets the output directory
def file_button_callback():
	filepath=filedialog.askdirectory()
	dir_var.set(filepath)
	dir_entry.delete(0,'end')
	dir_entry.insert(0,filepath)

root = tk.Tk()
root.title('Anki Audio Thief')
#root.geometry('600x400+50+50')

deck_frame  = ttk.Frame(root)
model_frame = ttk.Frame(root)
field_frame = ttk.Frame(root)
radio_frame = ttk.Frame(root)

deck_label  = ttk.Label(deck_frame, text="Select Deck",width=15)
model_label = ttk.Label(model_frame,text="Select Note",width=15)
field_label = ttk.Label(field_frame,text="Select Field",width=15)
radio_label = ttk.Label(radio_frame,text="| Select type",width=11)

deck_name = tk.StringVar()
deck_combo_box = ttk.Combobox(deck_frame, textvariable=deck_name,width=50)
deck_combo_box['values'] = get_deck_list()
deck_combo_box['state'] = 'readonly'
deck_combo_box.current(newindex=0)

model_name = tk.StringVar()
model_combo_box = ttk.Combobox(model_frame, textvariable=model_name,width=50)
model_combo_box['state'] = 'readonly'

field_name = tk.StringVar()
field_combo_box = ttk.Combobox(field_frame, textvariable=field_name,width=50)
field_combo_box['state'] = 'readonly'

should_delete_var = tk.IntVar()
should_delete_box = tk.Checkbutton(radio_frame,text="Delete stale output?",variable=should_delete_var,onvalue=1,offvalue=0)

radio_option = tk.IntVar()
radio_new    = tk.Radiobutton(radio_frame,text="Seen",variable=radio_option,value=1)
radio_learn  = tk.Radiobutton(radio_frame,text="Review",variable=radio_option,value=2)
radio_all    = tk.Radiobutton(radio_frame,text="All",variable=radio_option,value=3)
#radio_new    = tk.Radiobutton(radio_frame,text="New",variable=radio_option,value=4)
radio_option.set(1)


dir_var = StringVar()
dir_entry  = Entry(root,textvariable=dir_var)
dir_entry['state'] = 'disabled'
dir_button = Button(root, text="Output Directory",width=13,command=lambda:file_button_callback())

set_combo_box_items(model_combo_box,get_deck_models(deck_combo_box.get()))
set_combo_box_items(field_combo_box,get_fields(model_combo_box.get()))


deck_combo_box.bind('<<ComboboxSelected>>',lambda x: set_combo_box_items(model_combo_box,get_deck_models(deck_combo_box.get())),add="+")
deck_combo_box.bind('<<ComboboxSelected>>',lambda x: set_combo_box_items(field_combo_box,get_fields(model_combo_box.get())),add="+")
model_combo_box.bind('<<ComboboxSelected>>',lambda x: set_combo_box_items(field_combo_box,get_fields(model_combo_box.get())))

audio_button=tk.Button(root,text="Copy Files",
	command=lambda: copy_files(get_audio_file_list(deck_combo_box.get(),model_combo_box.get(),field_combo_box.get())))

deck_frame.pack(expand=True)
model_frame.pack(expand=True)
field_frame.pack(expand=True)
radio_frame.pack(expand=True)


deck_label.pack(side = LEFT,fill=tk.X, padx=5, pady=5)
deck_combo_box.pack(fill=tk.X,side = LEFT)

model_label.pack(side = LEFT,fill=tk.X, padx=5, pady=5)
model_combo_box.pack(side = LEFT,fill=tk.X)

field_label.pack(side = LEFT,fill=tk.X, padx=5, pady=5)
field_combo_box.pack(side = LEFT,fill=tk.X)

should_delete_box.pack(side = LEFT, fill=tk.X)

radio_label.pack(side = LEFT,fill=tk.X, padx=5, pady=5)
radio_new.pack(side = LEFT,fill=tk.X)
radio_learn.pack(side = LEFT,fill=tk.X)
radio_all.pack(side = LEFT,fill=tk.X)
#radio_new.pack(side = LEFT, fill=tk.X)

dir_button.pack(fill=tk.X, padx=5, pady=5)
dir_entry.pack(fill=tk.X)

audio_button.pack(expand=True)

root.mainloop()