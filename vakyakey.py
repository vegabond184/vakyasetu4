import customtkinter as ctk
import pyttsx3
from nltk import FreqDist, ngrams, word_tokenize
import re
import pyautogui
import time


STRINGS = {
    "English": {
        "title": "VakyaSetu", 
        "lang_tag": "English",
        "actions": ["Enter", "Clear", "Back", "Space"],
        "alphabets": [chr(65 + i) for i in range(26)] + ["Escape"]
        },

    "Hindi": {
        "title": "वाक्यसेतु",
        "lang_tag": "हिंदी",
        "actions":  ["बोलें", "साफ", "हटाएँ", "स्पेस", "बंद","भाषा बदलें"],
        "alphabets": [
                "अ","आ","इ","ई","उ",
                "ऊ","ए","ऐ","ओ","औ",
                "क","ख","ग","घ","ङ",
                "च","छ","ज","झ","ञ",
                "ट","ठ","ड","ढ","ण",
                "त","थ","द","ध","न",
                "प","फ","ब","भ","म",
                "य","र","ल","व",
                "श","ष","स","ह",
                "ा","ि","ी","ु","ू",
                "े","ै","ो","ौ","्"
        ] + ["Escape"]
        }


}



# ------------------------- NLP: WORD SUGGESTIONS -------------------------
def get_word_suggestions(text_corpus, current_word, num_suggestions=5):
    # Tokenize the text into lowercase words
    words = word_tokenize(text_corpus.lower())

    # Frequency distribution of all words
    freq = FreqDist(words)

    # Create bigrams (pairs of consecutive words)
    bigrams = list(ngrams(words, 2))

    # Get frequency of words that follow the current word (context-aware)
    next_word_freq = FreqDist([
        next_word for prev_word, next_word in bigrams
        if prev_word == current_word.lower()
    ])

    # If user typed something, find prefix-matching words
    if current_word:
        pattern = re.compile("^" + re.escape(current_word.lower()))
        possible_words = [w for w in freq.keys() if pattern.match(w)]
    else:
        possible_words = []

    # Sort suggestions by frequency of occurrence
    suggestions = [w.upper() for w in sorted(
        possible_words,
        key=lambda w: freq[w],
        reverse=True
    )[:num_suggestions]]

    # Also include bigram-based (contextual) suggestions
    suggestions_for_one = [word.upper() for word, _ in next_word_freq.most_common(num_suggestions)]

    return suggestions + suggestions_for_one



def speak(text):

    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)  # Slow down speech rate
    engine.setProperty('volume', 3)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id) 
    engine.say(text)
    engine.runAndWait()



def new_suggestions(word):
    
    words = []
    count = []  
    wordlist = open('wordlist.txt','r',encoding='utf-8') 
    corpus = wordlist.read()  #this will read already exist corpus file
    wordlist.close()

    usedWords = open('usedWords.txt','r',encoding='utf-8') #this will read the file which is keeping track of the used words and their counts
    usedWord = usedWords.readlines()

    for i in usedWord:
        words.append(i.split(":")[0])  #seprating words and counts
        count.append(int(i.split(":")[1].split("\n")[0]))
    usedWords.close()

    if word.capitalize() not in corpus and word.lower() not in corpus and word.capitalize() not in words: # checking if the word alredy in corpus or not
        with open("usedWords.txt",'a') as usedWord:
            usedWord.write(f"{word.capitalize()}:{1}\n")


    if word.capitalize() in words:
        count[words.index(word.capitalize())] = count[words.index(word.capitalize())] + 1 #incrementing the count 

        with open('usedWords.txt','w') as rewriting: #rewriting the whole file with incremented count
            for i in words:
                rewriting.write(f"{i}:{count[words.index(i)]}\n")
    

    for limit in count:
        if limit > 2:
        
            with open("wordlist.txt",'a') as wordList: #adding the new word to the main list
                wordList.write(f"\n{words[count.index(limit)]}\n")

            words.remove(words[count.index(limit)]) #removing the word and count of the added word
            count.remove(limit)

            words.append("reset") #for loop was not working with empty list
            count.append(0)
            

            for i in words:
                with open("usedWords.txt",'w') as rewriting: #rewriting the whole file
                    rewriting.write(f"{i}:{count[words.index(i)]}\n")




def new_suggestions_hindi(word):
    
    words = []
    count = []  
    wordlist = open('wordlist_hindi.txt','r',encoding="utf-8") 
    corpus = wordlist.read()  #this will read already exist corpus file
    wordlist.close()

    usedWords = open('usedWords_hindi.txt','r',encoding="utf-8")
    usedWord = usedWords.readlines()

    for i in usedWord:
        words.append(i.split(":")[0])  #seprating words and counts
        count.append(int(i.split(":")[1].split("\n")[0]))
    usedWords.close()

    if word not in corpus and word not in words: # checking if the word alredy in corpus or not
        speak("ok sir")
        with open("usedWords_hindi.txt",'a',encoding="utf-8") as usedWord:
            usedWord.write(f"{word.capitalize()}:{1}\n")


    if word.capitalize() in words:
        count[words.index(word.capitalize())] = count[words.index(word.capitalize())] + 1 #incrementing the count 

        with open('usedWords_hindi.txt','w',encoding="utf-8") as rewriting: #rewriting the whole file with incremented count
            for i in words:
                rewriting.write(f"{i}:{count[words.index(i)]}\n")
    

    for limit in count:
        if limit > 2:
        
            with open("wordlist_hindi.txt",'a',encoding="utf-8") as wordList: #adding the new word to the main list
                wordList.write(f"\n{words[count.index(limit)]}\n")

            words.remove(words[count.index(limit)]) #removing the word and count of the added word
            count.remove(limit)

            words.append("reset") #for loop was not working with empty list
            count.append(0)
            

            for i in words:
                with open("usedWords_hindi.txt",'w',encoding="utf-8") as rewriting: #rewriting the whole file
                    rewriting.write(f"{i}:{count[words.index(i)]}\n")




class AlphabetLocator:
    def __init__(self, root,language):
        
        self.root = root
        self.root.title(STRINGS[language]["title"])   
        self.language = language
        root.attributes('-fullscreen', True) 
        self.root.state("zoomed")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.mode = "matrix"

        # Grid configuration
        if self.language == "English":
            self.alphabet_rows = 7
            self.cols = 4
        elif self.language == "Hindi":
            self.alphabet_rows = 11
            self.cols = 5

        self.action_rows = 1
        self.rows = self.alphabet_rows + self.action_rows
        
        self.labels = []

        # Trackers
        self.current_row = 0
        self.current_col = 0
        self.stage = "col"  # Toggle between 'col' and 'row'
        self.selected_history = ""

        # Suggestion system
        self.suggestions = []
        self.suggestion_labels = []
        self.selected_index = -1

       
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Dynamic resizing
        total_rows = self.rows + 4
        for r in range(total_rows):
            self.main_frame.grid_rowconfigure(r, weight=1)
        for c in range(self.cols + 1):
            self.main_frame.grid_columnconfigure(c, weight=1)

       
        self.history_entry = ctk.CTkEntry(
            self.main_frame, font=("Arial", 26, "bold"), justify="left"
        )

        self.history_entry.focus_set()
        
        
        self.history_entry.grid(row=0, column=0, columnspan=self.cols+1, pady=10, padx=10, sticky="nsew")
        # self.history_entry.bind("<KeyRelease>", self.on_key_release_in_entry)
        # self.history_entry.bind("<Delete>", self.move_suggestion_down)
        self.history_entry.bind("<Down>", self.change_mode)
        # self.history_entry.bind("<Up>", self.move_suggestion_up)
        self.history_entry.bind("<Return>", self.confirm_suggestion_from_entry)
        self.history_entry.bind('<Map>', self.history_entry.focus_set())
        
        self.update_history()
        

       
        self.suggestion_box = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="gray20")
        self.suggestion_box.grid(row=1, column=0, columnspan=self.cols+1, sticky="nsew", padx=10)
        self.suggestion_box.grid_remove()  # Hidden by default

        # COLUMN AND ROW LABELS
        for c in range(self.cols):
            lbl = ctk.CTkLabel(self.main_frame, text=f"{c+1}", font=("Arial", 18, "bold"))
            lbl.grid(row=2, column=c+1, sticky="nsew", padx=5, pady=5)

        for r in range(self.rows):
            text = "Actions" if r == 0 else f"{r}"
            lbl = ctk.CTkLabel(self.main_frame, text=text, font=("Arial", 18, "bold"))
            lbl.grid(row=r+3, column=0, sticky="nsew", padx=5, pady=5)

        # Create main alphabet and action grid
        self.create_grid()
        

        # ------------------ STATUS BAR ------------------
        self.status = ctk.CTkLabel(self.main_frame, text="Select a column (← →)", font=("Arial", 18))
        self.status.grid(row=self.rows+3, column=0, columnspan=self.cols+1, sticky="nsew")

        self.highlight_selection()
        self.root.after(100, self.history_entry.focus_set)

        #KEYBOARD SHORTCUTS
        
        # Delete: Move Right(loop back to the first) and move down(loop back to the first)
        self.root.bind("<Delete>", self.matrix_navigation)
        self.root.bind("<Return>", self.confirm_selection)  # Enter → Confirm
        self.root.bind("<Escape>", lambda e: self.root.destroy())  # Escape → Exit


    #GRID CREATION
    def create_grid(self):
        """Create the grid layout for actions and alphabets."""
        self.labels = []

        # Action row (row 0)
        actions = STRINGS[self.language]["actions"]
        action_row = []
        for c in range(self.cols):
            lbl = ctk.CTkLabel(
                self.main_frame, text=actions[c], font=("Arial", 18, "bold"),
                fg_color="gray25", corner_radius=8
            )
            lbl.grid(row=3, column=c+1, sticky="nsew", padx=5, pady=5)
            action_row.append(lbl)
        self.labels.append(action_row)

        # Alphabet grid (A–Z)
        alphabets = STRINGS[self.language]["alphabets"]
        # alphabets.append("Escape")
        index = 0
        for r in range(1, self.rows):
            row_labels = []
            for c in range(self.cols):
                letter = alphabets[index] if index < len(alphabets) else ""
                lbl = ctk.CTkLabel(
                    self.main_frame, text=letter, font=("Arial", 24),
                    fg_color="gray15", corner_radius=8
                )
                lbl.grid(row=r+3, column=c+1, sticky="nsew", padx=5, pady=5)
                row_labels.append(lbl)
                index += 1
            self.labels.append(row_labels)
       
          
        

    #VISUAL SELECTION
    def highlight_selection(self):
        # Reset all colors
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0:
                    self.labels[r][c].configure(fg_color="gray25")
                else:
                    self.labels[r][c].configure(fg_color="gray15")
        
        if self.mode == "matrix":
            # Highlight based on stage
            if self.stage == "col":
                for r in range(self.rows):
                    self.labels[r][self.current_col].configure(fg_color="royalblue4")
                    # self.status.configure(text=f"Selected column: {self.current_col+1}. Now choose row (↑ ↓).")

            elif self.stage == "row":
                for c in range(self.cols):
                    self.labels[self.current_row][c].configure(fg_color="seagreen4")
                if self.current_row == 0:
                    self.status.configure(text="Selected Actions row. Press ENTER to perform action.")
                else:
                    self.status.configure(text=f"Selected row: {self.current_row}. Press ENTER to confirm.")

    #NAVIGATION CONTROLS

    def matrix_navigation(self, event):
        if self.mode == "matrix":
            if self.stage == "col":
                self.current_col = (self.current_col + 1) % self.cols
                self.highlight_selection()

            if self.stage == "row":
                self.current_row = (self.current_row + 1) % self.rows
                self.highlight_selection()



    #CONFIRMATION
    def confirm_selection(self, event):
    
        if self.stage == "col":
            self.stage = "row"
            self.highlight_selection()
            return

        # Get selected label text
        text = self.labels[self.current_row][self.current_col].cget("text")

        if text == "Escape":
            self.root.destroy()

        # Action row logic
        if self.current_row == 0:
            if text == "Clear" or text == "साफ":
                self.selected_history = ""
            elif text == "Back" or text == "हटाएँ":
                self.selected_history = self.selected_history[:-1]
            elif text == "Space" or text == "स्पेस":
                self.selected_history += " "
            elif text == "Enter" or text == "बोलें":
                speak(self.selected_history)
                if self.language == "English":
                    new_suggestions(self.selected_history)
                elif self.language == "Hindi":
                    new_suggestions_hindi(self.selected_history)
                    print("ok")
            self.update_history()

        # Alphabet input
        else:
            if text != "":
                self.selected_history += text
                self.update_history()
                # print(self.selected_history)
                

        # Reset selection stage
        self.root.after(800, self.reset_selection)
        self.show_autocomplete()
    
    def change_mode(self, event):
        if self.mode == "matrix":
            self.mode = "suggestion"
            self.reset_selection()
            self.history_entry.bind("<Delete>", self.move_suggestion_down)
        
            for r in range(self.rows):
                for c in range(self.cols):
                    if r == 0:
                        self.labels[r][c].configure(fg_color="gray25")
                    else:
                        self.labels[r][c].configure(fg_color="gray15")
            self.status.configure(text="Switched to suggestion mode. Use Up/Down to navigate suggestions.")
        
        else:
            self.mode = "matrix"
            self.root.bind("<Delete>", self.matrix_navigation)
            self.highlight_selection()
            self.status.configure(text="Switched to matrix mode. Select a column (← →).")



    def reset_selection(self):
        """Reset selection back to column stage."""
        self.stage = "col"
        self.current_row = 0
        self.current_col = 0
        self.highlight_selection()
        
        

    #ENTRY FIELD UPDATES
    def update_history(self):
        """Update the entry box text to match current user input."""
        self.history_entry.delete(0, "end")
        self.history_entry.insert(0, self.selected_history)

    #AUTOCOMPLETE 
    def on_key_release_in_entry(self, event):
        """Handle user typing in entry box and trigger autocomplete."""
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            return
        self.show_autocomplete()

    def show_autocomplete(self):
        """Display the autocomplete suggestion list."""
        typed = self.history_entry.get().strip()

        # Clear old suggestions
        for lbl in self.suggestion_labels:
            lbl.destroy()
        self.suggestion_labels = []
        self.suggestions = []
        self.selected_index = -1

        if not typed:
            self.suggestion_box.grid_remove()
            return

        if self.language == "Hindi":
             with open("wordlist_hindi.txt",'r',encoding="utf-8") as wordlist:
                corpus = wordlist.read()
        else:
            with open("wordlist.txt",'r') as wordlist:
                corpus = wordlist.read()

        last_word = typed.split()[-1] if typed.split() else ""
        self.suggestions = get_word_suggestions(corpus, last_word)
    
        if not self.suggestions:
            self.suggestion_box.grid_remove()
            return

        # Show suggestion box
        self.suggestion_box.grid()

        for i, word in enumerate(self.suggestions[:5]):
            lbl = ctk.CTkLabel(
                self.suggestion_box,
                text=word,
                font=("Arial", 18),
                fg_color="gray30",
                corner_radius=6
            )
            lbl.pack(fill="x", pady=2, padx=4)
            lbl.bind("<Button-1>", lambda e, w=word: self.select_suggestion(w))
            self.suggestion_labels.append(lbl)
        self.update_suggestion_highlight()

    #SUGGESTION CONTROL 
    def update_suggestion_highlight(self):
        """Highlight selected suggestion in the dropdown."""
        for i, lbl in enumerate(self.suggestion_labels):
            if i == self.selected_index:
                lbl.configure(fg_color="royalblue4")
            else:
                lbl.configure(fg_color="gray30")


    def move_suggestion_down(self, event):
        """Move suggestion highlight down."""
        # self.mode = "suggestion"
        if not self.suggestions:
            return None
        
        if self.mode == "suggestion":
            self.selected_index = (self.selected_index + 1) % len(self.suggestion_labels)
            self.update_suggestion_highlight()
            return "break"


    def confirm_suggestion_from_entry(self, event):
        """Confirm currently highlighted suggestion (via Tab)."""
        if not self.suggestions:
            return None
        if self.selected_index != -1:
            
            chosen = self.suggestions[self.selected_index]
            self.select_suggestion(chosen)
            self.show_autocomplete()

            return "break"
        
        # self.selected_index = -1

    def select_suggestion(self, word):
        """Insert the selected suggestion into the entry field."""
        current_text = self.history_entry.get()
        tokens = current_text.split()

        # Remove isolated letters (cleanup)
        for token in tokens:
            if len(token) == 1 and token != "I":
                tokens.remove(token)

        self.selected_history = " ".join(tokens)

        # Append chosen word
        if tokens:
            self.selected_history += " " + word + " "
        else:
            self.selected_history = word

        self.update_history()



def main(language):
    app = ctk.CTk()
    AlphabetLocator(app,language=language)
    app.mainloop()
    
