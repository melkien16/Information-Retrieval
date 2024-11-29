import re
import sys
import os
from tkinter import font
import numpy as np
from collections import Counter, defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QLabel, QFrame, QPushButton
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt

import tkinter as tk
from tkinter import filedialog
import fitz

# Define the word pattern for tokenization
pattern = r"\b(?:[a-zA-Z]+(?:’[a-zA-Z]+)?)\b"
selected_pdf_file = ''

class PDFSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF File Selector")

        # Set the width and height of the window
        window_width = 600
        window_height = 400
        self.root.geometry(f"{window_width}x{window_height}")

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        # Create a label to display messages
        self.label = tk.Label(root, text="Select a PDF file to open", wraplength=350, font=font.Font(family='Helvetica', size=20, weight='bold'))
        self.label.pack(pady=20)

        # Create a button to open the file dialog
        self.select_button = tk.Button(root, text="Select PDF File", command=self.select_pdf_file,
                                       font=("Arial", 16, "bold"), fg="white", bg="green", width=20, height=2)
        self.select_button.pack(pady=10)
        self.select_button.bind("<Enter>", self.on_enter)
        self.select_button.bind("<Leave>", self.on_leave)

        # Button to switch to PyQt5 GUI
        self.switch_button = tk.Button(root, text="Open IR System", command=self.open_ir_system,
                                       font=("Arial", 16, "bold"), fg="white", bg="blue", width=20, height=2)
        self.switch_button.pack(pady=10)
        self.switch_button.bind("<Enter>", self.on_enter)
        self.switch_button.bind("<Leave>", self.on_leave)

        # Create the "Close System" button
        self.add_button = tk.Button(root, text="Close System", command=self.add_and_close,
                                    font=("Arial", 16, "bold"), fg="white", bg="red", width=20, height=2)
        self.add_button.bind("<Enter>", self.on_enter)
        self.add_button.bind("<Leave>", self.on_leave)

    def select_pdf_file(self):
        global selected_pdf_file
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            selected_pdf_file = file_path
            self.label.config(text=f"Selected PDF file: {os.path.basename(selected_pdf_file)}")
            self.add_button.pack(pady=10)  # Show the "Add" button

    def add_and_close(self):
        self.root.destroy()

    def open_ir_system(self):
        self.root.destroy()
        app = QApplication(sys.argv)
        ex = IRSystemGUI()
        ex.show()
        sys.exit(app.exec_())

    def on_enter(self, event):
        event.widget.config(bg="darkgrey")

    def on_leave(self, event):
        if event.widget == self.select_button:
            event.widget.config(bg="green")
        elif event.widget == self.switch_button:
            event.widget.config(bg="blue")
        elif event.widget == self.add_button:
            event.widget.config(bg="red")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def tokenize_word(text):
    tokens = re.findall(pattern, text)
    tokens_lower = [token.lower() for token in tokens]
    words = tokens_lower
    return words

def remove_stopwords(text):
    stop_words = {"aanee", "gidduu", "itti", "narraa", "akka", "gubbaa", "ittuu", "natti", "akkam", "hanga", "jala", "nu","akkasumas", "henna", "jara", "nurraa", "akkuma", "hogguu", "sana", "nuti","ala", "illee", "kan", "siin","alatti", "immoo", "kana", "silaa","amma", "inni", "kanaafi", "kanaaf", "sitti","ammoo", "irra", "kanaafuu", "sun","an", "isaa", "kee", "tanaaf","ani", "isaaf", "keenna", "tanaafuu", "ati", "isaanirraa", "keessa", "ta'ullee", "tira", "isatti", "keessan", "teenya", "booda", "tun", "keenya", "utuu", "booddee", "iseen", "keessatti", "waan","dura", "ishii", "kiyya", "warra", "duuba", "ishiif", "koo", "yeroo", "eega", "ishiirraa", "yommuu", "eegasii", "isii", "malee", "yoo", "fi", "isin", "na", "yookaan", "gama", "isiin", "naaf", "yoom", "kun","gara","hin","isaani","tokko","ilaalcha","ture","oljirraa","isa","obbo","garuu","ni","osoo","yo","malee","isaan",""}
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    filtered_text = ' '.join(filtered_words)
    return filtered_text

def stemming(word):
    prefixes = ['armaan','dhe']
    suffixes = ['iin','iff','arra','bira','irra','itti', 'dha', 'n', 'lee', 'icha', 'tu', 'oo', 'oota', 'wwan', 'achu', 'eenyaa', 'ina','ummaa','an', 'een', 'eeyyii', 'jala', 'rre','suuf','ooli','duuba', 'f', 'ooffuu', 'fu', 'suu', 'ssuu', 'na','ii','leen','iis','isaa','duraa','dhaa','msaa','is', 'ia', 'tta']

     # Substitution rules: (pattern, replacement)
    substitutions = [
        ("ee", "a"),  
        ("oonni", "a"),  
        ("oota", "a"),   
        ("ootni", "a"),    
        ("neen", "a"),          
        ("eenya", "u"),      
        ("uun", "a"),      
        ("ota", "o"),      
        ("an", "u"),      
        ("le", "u"),      
        ("ni", "a"),      
        ("inuu", "a"), 
        ("i", "a") ,     
        ("ti", "a"),      
        ("dhanii", "u"),      
        ("dhame", "e"),      
        ("umaa", "a"),      
        ("oonnis", "a"),      
        ("ootaa", "a"),      
        ("eeyyii", "u"),      
        ("aachuu", "u"),      
        ("oonn", "ee"),      
        ("naa", "a"),      
        ("otni", "a"),      
        ("amu", "u"),      
        ("si", "a"),      
        ("te", "chu"),      
        ("chisu", "chu"),      
        ("ootni", "a"),      
        ("dhamee", "chu"),      
        ("uma", "a"),     
        ("ni", "a"),      
        ("atee", "u"),      
        ("lii", "aa"),      
        ("uma", "u"),      
        ("amu", "a"),      
        ("isaa", "u"),      
        ("te", "chu"),      
        ("mii", "u"),      
        ("oo", "a"),     
        ("onni", "a"),      
        ("anii", "a"),      
        ("nnoo", "chu"),      
        ("amaa", "u"),      
        ("icha", "a"),      
        ("keen", "a"),      
        ("chuma", "a"),      
        ("an", "u"),           
        ("han", "u"),     
    ]

    substitutions2 = [
        ("au", 'aa')
    ]

    for prefix in prefixes:
        if word.startswith(prefix):
            word = word[len(prefix):]
            break

    for pattern, replacement in substitutions:
        if len(word) < 4:
            return word
        else:
            if word.endswith(pattern):
                word = word[:-len(pattern)] + replacement
                break  

    for suffix in suffixes:
            if len(word) < 5:
                return word
            else:
                if word.endswith(suffix):
                    word = word[:-len(suffix)]
                    break

    for pattern, replacement in substitutions2:
        if len(word) < 5:
            return word
        else:
            if word.endswith(pattern):
                word = word[:-len(pattern)] + replacement
                break
    return word

def preprocess(text):
    tokenized_words = tokenize_word(text)
    text_without_stopwords = remove_stopwords(" ".join(tokenized_words))
    removed_stop_word = text_without_stopwords.split()
    stemmed_text = [stemming(word) for word in removed_stop_word]
    return stemmed_text

def create_inverted_index(documents):
    inverted_index = defaultdict(list)
    
    for doc_id, text in enumerate(documents, start=1):
        words = text.split()
        for word in words:
            if doc_id not in inverted_index[word]:
                inverted_index[word].append(doc_id)
    
    return inverted_index

def compute_tf(documents):
    tf = []
    for text in documents:
        tokens = preprocess(text)
        token_count = Counter(tokens)
        tf.append(token_count)
    return tf

def create_document_vectors(tf, vocabulary):
    vectors = []
    for doc_tf in tf:
        vector = [doc_tf.get(term, 0) for term in vocabulary]
        vectors.append(vector)
    return np.array(vectors)

def compute_cosine_similarity(query, document_vectors, vocabulary):
    query_processes = preprocess(query)
    query_tf = Counter(query_processes)
    query_vector = np.array([query_tf.get(term, 0) for term in vocabulary]).reshape(1, -1)

    similarities = cosine_similarity(query_vector, document_vectors)
    return similarities.flatten()

# def highlight_text(text_edit, words):
#     cursor = text_edit.textCursor()
#     format = QTextCharFormat()
#     format.setBackground(QColor("#FFFF00"))  # Yellow highlight

#     for word in words:
#         cursor.setPosition(0)
#         while True:
#             cursor = text_edit.document().find(word, cursor)
#             if cursor.isNull():
#                 break
#             start = cursor.selectionStart()
#             cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
#             if cursor.selectedText().startswith(word):
#                 cursor.mergeCharFormat(format)
#             cursor.setPosition(start + len(word))

class IRSystemGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mini Information Retrieval System')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Search Input
        search_frame = QFrame()
        search_layout = QVBoxLayout()
        search_frame.setLayout(search_layout)

        search_label = QLabel("Enter your query here:")
        self.queryInput = QLineEdit()
        self.queryInput.setPlaceholderText("Search...")
        self.queryInput.textChanged.connect(self.search)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.queryInput)

        main_layout.addWidget(search_frame)

        # Results Display
        self.resultDisplay = QTextEdit()
        self.resultDisplay.setReadOnly(True)
        main_layout.addWidget(self.resultDisplay)

        # Button to switch back to Tkinter PDF Selector
        self.switch_button = QPushButton("Select another PDF")
        self.switch_button.clicked.connect(self.open_pdf_selector)
        main_layout.addWidget(self.switch_button)

        self.setLayout(main_layout)

        self.setStyleSheet(
            "QFrame { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 5px; padding: 10px; }"
            "QLabel { font-size: 20px; font-weight: bold; color: #333; }"
            "QLineEdit { border: 1px solid #ccc; border-radius: 3px; padding: 8px; font-size: 18px; color: #555; }"
            "QTextEdit { border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 16px; color: #333; }"
            "QPushButton { padding: 10px; font-size: 18px; }"
        )

        if selected_pdf_file:
            self.process_pdf(selected_pdf_file)

    def process_pdf(self, pdf_path):
        extracted_text = extract_text_from_pdf(pdf_path)
        processed_words = preprocess(extracted_text)
        
        # Split text into documents (this can be adjusted as needed)
        chunk_size = len(processed_words) // 4
        documents = [' '.join(processed_words[i:i + chunk_size]) for i in range(0, len(processed_words), chunk_size)]
        
        tf = compute_tf(documents)
        vocabulary = sorted(set(word for doc_tf in tf for word in doc_tf))
        global document_vectors
        document_vectors = create_document_vectors(tf, vocabulary)
        global documents_global
        documents_global = documents
        global vocabulary_global
        vocabulary_global = vocabulary
        inverted_index = create_inverted_index(documents)
        global inverted_index_global
        inverted_index_global = inverted_index

    def returnInvertedIndex(self):
        return inverted_index_global

    def search(self):
        query = self.queryInput.text()
        if query.strip() and 'documents_global' in globals():  # Only search if the query is not empty
            similarities = compute_cosine_similarity(query, document_vectors, vocabulary_global)
            ranked_doc_indices = np.argsort(similarities)[::-1]

            results = "<div style='font-size: 20px; color: #333;'>Documents ranked by their similarity to the query:</div><br>"
            search_terms = preprocess(query)

            for idx in ranked_doc_indices:
                doc_text = documents_global[idx]
                results += f"<div style='font-size: 20px; color: #0066cc;'><b>Document {idx + 1}:</b></div>"
                # highlighted_text_edit = QTextEdit()
                # highlighted_text_edit.setPlainText(doc_text)
                # highlight_text(highlighted_text_edit, search_terms)
                # results += f"{highlighted_text_edit.toHtml()}<br>"
                results += f"<div style='font-size: 18px; color: #333;'><b>Similarity:</b> {similarities[idx]:.4f}</div><br>"
                results += "<div style='font-size: 18px; color: #333;'><b>Occurrences:</b></div>"

                # positions = []
                # words = preprocess(doc_text)
                # for term in search_terms:
                #     positions += [(term, i) for i, word in enumerate(words) if word.startswith(term)]

                # for term, pos in positions:
                #     results += f"<div style='font-size: 18px; color: #333;'>'{term}' at position {pos}</div>"

                # results += "<br>"

            self.resultDisplay.setHtml(results)
        else:
            self.resultDisplay.clear()

    def open_pdf_selector(self):
        self.close()
        root = tk.Tk()
        PDFSelector(root)
        root.mainloop()


if __name__ == '__main__':
    # Start with the Tkinter PDF selector
    root = tk.Tk()
    pdf_selector = PDFSelector(root)
    root.mainloop()