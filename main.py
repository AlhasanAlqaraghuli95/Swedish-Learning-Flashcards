import tkinter as tk
import pandas as pd
import random
from pathlib import Path

BACKGROUND_COLOR = "#B1DDC6"

FONT = "arial"
LANG_WEIGHT = "italic"
LANG_SIZE = 24

WORD_WEIGHT = "bold"
WORD_SIZE = 60
SV_FILL = "black"
EN_FILL = "white"

TIME = 3000


# ---------------------------- DATA IMPORT ------------------------------- #
vocabulary_file_path = Path('data') / '1000 most common sv words.csv'
vocabulary = pd.read_csv(vocabulary_file_path)

# converting the data into a dictionary
vocab_dict = vocabulary.to_dict(orient = 'records') 

# store already displayed words into a list
displayed_words = []

# store correctly guessed words into a list
file_guessed = Path('data') / 'correctly_guessed.csv' # the file path

try:
    loaded_guessed_words = pd.read_csv(file_guessed) # load the file into a dataframe (Read)
     
except FileNotFoundError:
    loaded_guessed_words = []
except pd.errors.EmptyDataError:
    loaded_guessed_words = []

guessed_words = []

# ---------------------------- FLASHCARD LOGIC ------------------------------- #

def on_closing():

    global guessed_words
    global loaded_guessed_words
    
    new_data = pd.DataFrame(guessed_words) # Save the newly guessed words into a separate df  (pre-update)

    try:
        data = pd.concat([loaded_guessed_words, new_data]) # Now add the new data to the old guessed words (Update)

    except NameError:
        data = new_data   
    
    except TypeError:
        data = new_data  

    data.to_csv(file_guessed, index=False)  # dump the data into the file (Save)

    window.destroy()

def correct_guess():
    global displayed_words
    global guessed_words
    global vocab_dict

    try: 
        guessed = vocab_dict[displayed_words[-1]] # Retrieve the last guessed word
    except IndexError:
        pass
    else:
        guessed_words.append(guessed)  # Add it to the list of guessed words

    change_word()

def wrong_guess():
    change_word()

def change_word():

    global switch
    
    window.after_cancel(switch) # cancel the previously scheduled call to flip the card

    swedish_word = choose_word()
    
    # Flip the card to front, and add the word onto it
    
    canvas.itemconfig(card, image = card_front_image)
    canvas.itemconfig(language_text, text = 'Svenska')
    canvas.itemconfig(word_text, text = swedish_word)

    switch = window.after(3000, show_english)


def choose_word():

    # Access the data and displayed words
    global vocab_dict
    global displayed_words
    global loaded_guessed_words

    # Choose a random number from within the bounds of the list
    choice = random.randint(0, len(vocab_dict)-1)

    # Make sure it wasn't already displayed
    while choice in displayed_words:
        choice = random.randint(0, len(vocab_dict)-1)

    # Make sure it wasn't already guessed correctly (comparing swedish word from vocab list to ones in guessed words df)
    try:
        if not loaded_guessed_words.empty:
            guessed_words_svenska = loaded_guessed_words['svenska'].tolist()

            while vocab_dict[choice]['svenska'] in guessed_words_svenska:
                choice = random.randint(0, len(vocab_dict)-1)

    except AttributeError:
        pass

    # Add this word to displayed words
    displayed_words.append(choice)

    swedish_word = vocab_dict[choice]['svenska']

    return swedish_word


def show_english():

    # Flip the card to back and show the english word
    # We do this by checking what word was displayed last
    # if nothing was displayed yet, show "Word"
    try: 
        english_word = vocab_dict[displayed_words[-1]]['english']
    except IndexError:
        canvas.itemconfig(card, image = card_back_image)
        canvas.itemconfig(language_text, text = 'English')
        canvas.itemconfig(word_text, text = "Word")
    else:
        canvas.itemconfig(card, image = card_back_image)
        canvas.itemconfig(language_text, text = 'English')
        canvas.itemconfig(word_text, text = english_word)
        

# ---------------------------- UI SETUP ------------------------------- #

# Creating the app window

window = tk.Tk()
window.title("Password Manager")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

# Creating the card

canvas = tk.Canvas(width = 800, height = 530, bg = BACKGROUND_COLOR, highlightthickness = 0)
canvas.grid(column = 0, row = 0, columnspan=2)

card_front_image_file_path = Path('images') / 'card_front.png'
card_front_image = tk.PhotoImage(file = card_front_image_file_path)

card_back_image_file_path = Path('images') / 'card_back.png'
card_back_image = card_back_image_file_path

# The tuple for create image specifies the x and y coordinates of the center of the image.
# setting it to half the canvas size will center the image

card = canvas.create_image(400, 265, image=card_front_image)

# Text on the flashcard
language_text = canvas.create_text(400, 150, text = "Svenska", font = (FONT, LANG_SIZE, LANG_WEIGHT), fill = SV_FILL)
word_text = canvas.create_text(400, 265, text = "Ord", font = (FONT, WORD_SIZE, WORD_WEIGHT), fill = SV_FILL)


# Buttons
correct_img_file_path = Path('images') / 'right.png'
correct_img = tk.PhotoImage(file = correct_img_file_path)

false_img_file_path = Path('images') / 'wrong.png'
false_img = tk.PhotoImage(file = false_img_file_path)

correct_button = tk.Button(image = correct_img, highlightthickness=0, borderwidth=0, command = correct_guess)
correct_button.grid(column=1, row=1)

false_button = tk.Button(image = false_img, highlightthickness=0, borderwidth=0, command = wrong_guess)
false_button.grid(column=0, row=1)

# Switch to English after a pause
switch = window.after(3000, show_english)

# call on_closing() when the window is closed
window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()
