# -*- coding: utf-8 -*-
"""
KI-Assistent Deluxe – Ultimative Version mit modernem Design, erweiterten Funktionen 
und optimierten Antworten für eine natürliche und nahtlose Kommunikation.
Completely free of charge - no external APIs required.
"""

import sys
import os
import logging
import time
import datetime
import webbrowser
import random
import re
import threading
from collections import deque

try:
    # Try to import PyQt5 for GUI version
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
        QPushButton, QWidget, QLabel, QScrollArea, QSplitter, QFrame, QToolBar,
        QAction, QStatusBar, QMenu, QMessageBox, QDialog, QComboBox, QCheckBox,
        QSpinBox, QTabWidget
    )
    from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
    from PyQt5.QtGui import QIcon, QPixmap, QTextCursor, QColor, QFont, QPalette
    from PyQt5.QtSvg import QSvgWidget
    GUI_AVAILABLE = True
except ImportError:
    # If PyQt5 is not available, we'll use the CLI version
    GUI_AVAILABLE = False

try:
    # Try to import transformers for better responses if available
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    filename='ki_assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ASCII Art for CLI version
ASCII_LOGO = """
 ██ ▄█▀ ██▓    ▄▄▄        ██████   ██████  ██▓  ██████ ▄▄▄█████▓ ▄▄▄       ███▄    █ ▄▄▄█████▓
 ██▄█▒ ▓██▒   ▒████▄    ▒██    ▒ ▒██    ▒ ▓██▒▒██    ▒ ▓  ██▒ ▓▒▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒
▓███▄░ ▒██░   ▒██  ▀█▄  ░ ▓██▄   ░ ▓██▄   ▒██▒░ ▓██▄   ▒ ▓██░ ▒░▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░
▓██ █▄ ▒██░   ░██▄▄▄▄██   ▒   ██▒  ▒   ██▒░██░  ▒   ██▒░ ▓██▓ ░ ░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ 
▒██▒ █▄░██████▒▓█   ▓██▒▒██████▒▒▒██████▒▒░██░▒██████▒▒  ▒██▒ ░  ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ 
▒ ▒▒ ▓▒░ ▒░▓  ░▒▒   ▓▒█░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░▓  ▒ ▒▓▒ ▒ ░  ▒ ░░    ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   
░ ░▒ ▒░░ ░ ▒  ░ ▒   ▒▒ ░░ ░▒  ░ ░░ ░▒  ░ ░ ▒ ░░ ░▒  ░ ░    ░      ▒   ▒▒ ░░ ░░   ░ ▒░    ░    
░ ░░ ░   ░ ░    ░   ▒   ░  ░  ░  ░  ░  ░   ▒ ░░  ░  ░    ░        ░   ▒      ░   ░ ░   ░      
░  ░       ░  ░     ░  ░      ░        ░   ░        ░                 ░  ░         ░          
                                                                                               
██████  ███████ ██      ██    ██ ██   ██ ███████                                               
██   ██ ██      ██      ██    ██  ██ ██  ██                                                    
██   ██ █████   ██      ██    ██   ███   █████                                                 
██   ██ ██      ██      ██    ██  ██ ██  ██                                                    
██████  ███████ ███████  ██████  ██   ██ ███████                                               
"""

class SimpleResponseGenerator:
    """Simple response generator that doesn't require external dependencies."""
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hallo! Wie kann ich dir heute helfen?",
                "Guten Tag! Wobei kann ich behilflich sein?",
                "Hi! Ich bin dein KI-Assistent. Was möchtest du wissen?",
                "Willkommen zurück! Wie kann ich dir assistieren?"
            ],
            "farewell": [
                "Bis bald! Melde dich, wenn du weitere Hilfe brauchst.",
                "Auf Wiedersehen! Ich bin hier, wenn du mich brauchst.",
                "Tschüss! Komm jederzeit zurück, wenn du Fragen hast.",
                "Bis zum nächsten Mal! Schönen Tag noch!"
            ],
            "thanks": [
                "Gerne! Ich freue mich, helfen zu können.",
                "Kein Problem! Gibt es noch etwas, womit ich dir helfen kann?",
                "Immer wieder gern! Weitere Fragen?",
                "Es ist mir ein Vergnügen zu helfen!"
            ],
            "weather": [
                "Ich kann leider keine Echtzeit-Wetterdaten abrufen, aber ich empfehle dir wetter.com oder eine ähnliche Webseite zu besuchen.",
                "Für aktuelle Wetterinformationen besuche bitte eine Wetter-App oder -Webseite.",
                "Wetterdaten kann ich nicht direkt anzeigen, aber ich kann dir helfen, eine Wetterseite zu öffnen."
            ],
            "time": [
                f"Die aktuelle Systemzeit ist {datetime.datetime.now().strftime('%H:%M:%S')}.",
                f"Es ist jetzt {datetime.datetime.now().strftime('%H:%M')} Uhr.",
                f"Die Uhrzeit beträgt {datetime.datetime.now().strftime('%H:%M')} Uhr."
            ],
            "date": [
                f"Heute ist der {datetime.datetime.now().strftime('%d.%m.%Y')}.",
                f"Das heutige Datum ist {datetime.datetime.now().strftime('%d. %B %Y')}.",
                f"Wir haben den {datetime.datetime.now().strftime('%d.%m.%Y')}."
            ],
            "capabilities": [
                "Ich kann dir mit grundlegenden Informationen helfen, Programme öffnen, Webseiten aufrufen und einfache Fragen beantworten.",
                "Meine Fähigkeiten umfassen das Öffnen von Programmen, Websuche, und die Beantwortung einfacher Fragen.",
                "Ich kann dir bei verschiedenen Aufgaben helfen, wie Websuche, Programme starten und Informationen bereitstellen."
            ],
            "unknown": [
                "Entschuldige, ich bin mir nicht sicher, wie ich darauf antworten soll. Kann ich dir mit etwas anderem helfen?",
                "Diese Frage ist für mich schwierig zu beantworten. Kannst du sie anders formulieren?",
                "Ich verstehe deine Anfrage leider nicht vollständig. Magst du es anders ausdrücken?",
                "Darauf habe ich leider keine passende Antwort. Gibt es etwas anderes, womit ich dir helfen kann?"
            ]
        }
        
        # Keyword mapping for responses
        self.keywords = {
            "greeting": ["hallo", "hi", "guten tag", "guten morgen", "hey", "servus", "moin"],
            "farewell": ["tschüss", "auf wiedersehen", "bye", "ciao", "bis später", "bis bald"],
            "thanks": ["danke", "vielen dank", "besten dank", "dankeschön"],
            "weather": ["wetter", "temperatur", "regnet", "schneit", "sonne"],
            "time": ["uhrzeit", "wie spät", "wie viel uhr"],
            "date": ["datum", "welcher tag", "tag heute", "kalender"],
            "capabilities": ["was kannst du", "fähigkeiten", "funktionen", "helfen", "hilf mir", "was machst du"]
        }
        
        # Extended responses for specific topics
        self.extended_responses = {
            "computer": "Computer sind elektronische Geräte, die Daten verarbeiten und speichern können. Sie bestehen aus Hardware (physische Komponenten) und Software (Programme und Betriebssysteme). Computer sind für viele Aufgaben unerlässlich geworden, von einfachen Berechnungen bis hin zu komplexen Simulationen und künstlicher Intelligenz.",
            
            "internet": "Das Internet ist ein weltweites Netzwerk aus miteinander verbundenen Computern, das den Austausch von Informationen und Kommunikation ermöglicht. Es wurde in den 1960er Jahren entwickelt und hat sich zu einem integralen Bestandteil des modernen Lebens entwickelt, der E-Mails, Webseiten, soziale Medien und vieles mehr umfasst.",
            
            "künstliche intelligenz": "Künstliche Intelligenz (KI) bezieht sich auf Computersysteme, die Aufgaben ausführen können, die normalerweise menschliche Intelligenz erfordern. Dazu gehören Spracherkennung, Entscheidungsfindung, Übersetzung und vieles mehr. KI kann in regelbasierte Systeme und maschinelles Lernen unterteilt werden, wobei letzteres Algorithmen verwendet, die aus Daten lernen können.",
            
            "python": "Python ist eine interpretierte, hochrangige Programmiersprache, die für ihre einfache Lesbarkeit und vielseitige Anwendbarkeit bekannt ist. Sie wird häufig in Bereichen wie Webentwicklung, Datenanalyse, künstliche Intelligenz und wissenschaftliche Berechnungen eingesetzt.",
            
            "gesundheit": "Gesundheit umfasst das körperliche, geistige und soziale Wohlbefinden. Eine gesunde Lebensweise beinhaltet ausgewogene Ernährung, regelmäßige körperliche Aktivität, ausreichend Schlaf und Stressbewältigung. Bei gesundheitlichen Bedenken solltest du immer einen Arzt konsultieren.",
            
            "musik": "Musik ist eine Kunstform, die Töne und Klänge in einer strukturierten und bewussten Weise organisiert. Sie kann verschiedene Emotionen ausdrücken und ist in allen Kulturen weltweit zu finden. Es gibt zahlreiche Musikgenres wie Klassik, Rock, Pop, Jazz, Hip-Hop und elektronische Musik."
        }
    
    def generate_response(self, user_text, chat_history=None):
        """
        Generates a contextual response based on user input and chat history.
        
        Args:
            user_text (str): The user's input text
            chat_history (list): Previous chat messages
            
        Returns:
            str: A generated response
        """
        user_text_lower = user_text.lower()
        
        # Check for keyword matches
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in user_text_lower:
                    return random.choice(self.responses[category])
        
        # Check for extended response topics
        for topic, response in self.extended_responses.items():
            if topic in user_text_lower:
                return response
        
        # Time-based greeting
        hour = datetime.datetime.now().hour
        if hour < 12 and "morgen" in user_text_lower:
            return "Guten Morgen! Wie kann ich dir an diesem Morgen behilflich sein?"
        elif 12 <= hour < 18 and "tag" in user_text_lower:
            return "Guten Tag! Wie geht es dir heute?"
        elif hour >= 18 and ("abend" in user_text_lower or "nacht" in user_text_lower):
            return "Guten Abend! Wie kann ich dir an diesem Abend helfen?"
        
        # Generate question response
        if "?" in user_text:
            if any(word in user_text_lower for word in ["wie", "was", "warum", "weshalb", "wo", "wann", "wer"]):
                return "Das ist eine interessante Frage. Ich habe zwar keine Verbindung zum Internet, kann dir aber mit grundlegenden Informationen helfen. Könntest du deine Frage konkretisieren oder nach einem bestimmten Thema fragen?"
        
        # If no specific response is found, return a general one
        return random.choice(self.responses["unknown"])


class TransformerResponseGenerator:
    """Response generator using HuggingFace Transformers library."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = "EleutherAI/pythia-410m"  # Smaller model to save resources
        self.max_length = 100
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize model during class initialization
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model and tokenizer."""
        try:
            logging.info(f"Loading model {self.model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            logging.info("Model loaded successfully.")
            return True
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}", exc_info=True)
            return False
    
    def is_model_loaded(self):
        """Check if the model is loaded."""
        return self.model is not None and self.tokenizer is not None
    
    def generate_response(self, user_text, chat_history=None):
        """
        Generate a response using the transformer model.
        
        Args:
            user_text (str): The user's input text
            chat_history (list): Previous chat messages
            
        Returns:
            str: A generated response
        """
        if not self.is_model_loaded():
            if not self._initialize_model():
                return "Entschuldigung, ich konnte das Sprachmodell nicht laden. Ich verwende stattdessen einfache Antworten."
        
        # Prepare the prompt with strict instructions for clear, coherent German responses
        prompt = (
            "Du bist ein intelligenter deutscher Assistent. "
            "Deine Antworten sind immer klar, präzise und bleiben strikt beim Thema. "
            "Du antwortest ausschließlich auf Deutsch, ohne Sprachmischung. "
            "Deine Antworten sind kurz, direkt und hilfreich. "
            "Du wiederholst dich nicht und sprichst nicht über Themen, die nicht angefragt wurden. "
            "\n\n"
            f"Benutzer: {user_text}\n"
            "Assistent:"
        )
        
        try:
            # Generate response with more conservative settings
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Create attention mask
            attention_mask = torch.ones_like(inputs.input_ids)
            
            output = self.model.generate(
                inputs.input_ids,
                attention_mask=attention_mask,
                max_length=len(inputs.input_ids[0]) + self.max_length,
                num_return_sequences=1,
                temperature=0.6,        # Lower temperature for more focused responses
                top_p=0.85,             # More conservative sampling
                repetition_penalty=1.5,  # Stronger penalty for repetition
                no_repeat_ngram_size=3,  # Prevent repeating 3-grams
                do_sample=True,
                early_stopping=True
            )
            
            # Decode the response
            response = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Clean up the response
            response = response.replace(prompt, "").strip()
            
            # Post-process to ensure quality
            response = self._post_process_response(response)
            
            # Ensure response is in German and relevant
            if not response or len(response) < 5:
                return "Entschuldigung, ich konnte keine passende Antwort generieren."
            
            return response
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}", exc_info=True)
            return "Entschuldigung, bei der Generierung der Antwort ist ein Fehler aufgetreten."
            
    def _post_process_response(self, response):
        """
        Post-processes the generated response to ensure it's clear and coherent.
        
        Args:
            response (str): The raw generated response
            
        Returns:
            str: Processed response
        """
        # Remove any non-German parts (simplistic but can catch obvious cases)
        non_german_markers = ["In English:", "Spanish:", "French:", "Italian:"]
        for marker in non_german_markers:
            if marker in response:
                response = response.split(marker)[0].strip()
        
        # Remove repetitions of the same sentence
        lines = response.split('.')
        processed_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in processed_lines:
                processed_lines.append(line)
        
        # If response became too short after processing, return a default
        if not processed_lines:
            return "Ich verstehe. Wie kann ich weiter helfen?"
            
        # Rejoin with proper spacing and punctuation
        response = '. '.join(processed_lines)
        if not response.endswith('.') and not response.endswith('?') and not response.endswith('!'):
            response += '.'
            
        return response


def clean_response(response, prompt=""):
    """
    Cleans up the response by removing the prompt part and unnecessary whitespace.
    
    Args:
        response (str): The response to clean
        prompt (str): Optional prompt to remove from the beginning
        
    Returns:
        str: Cleaned response
    """
    if prompt and response.startswith(prompt):
        response = response[len(prompt):]
        
    # Remove any special tokens
    response = re.sub(r"<.*?>", "", response)
    
    # Clean up excessive whitespace
    response = re.sub(r"\s+", " ", response)
    
    return response.strip()


def parse_command(user_text):
    """
    Parses user input to identify commands.
    
    Args:
        user_text (str): The user's input text
        
    Returns:
        tuple: (command_type, command_args) or (None, None) if no command is detected
    """
    user_text = user_text.strip().lower()
    
    if user_text.startswith("öffne url") or user_text.startswith("offne url"):
        return "open_url", user_text.replace("öffne url", "").replace("offne url", "").strip()
    elif user_text.startswith("öffne") or user_text.startswith("offne"):
        return "open_program", user_text.replace("öffne", "").replace("offne", "").strip()
    elif user_text.startswith("suche"):
        return "search", user_text.replace("suche", "").strip()
    elif user_text == "hilfe" or user_text == "help":
        return "help", None
    elif user_text == "lösche chat" or user_text == "losche chat" or user_text == "clear":
        return "clear_chat", None
    elif user_text == "exit" or user_text == "quit" or user_text == "beenden":
        return "exit", None
    
    return None, None


def get_help_text():
    """
    Returns help text with available commands.
    
    Returns:
        str: Formatted help text
    """
    help_text = """
    Verfügbare Befehle:
    - öffne [programm]: Öffnet ein Programm (z.B. notepad, calc, explorer)
    - öffne url [webadresse]: Öffnet eine Webseite
    - suche [suchbegriff]: Sucht nach Informationen
    - hilfe: Zeigt diese Hilfe an
    - lösche chat: Löscht den Chat-Verlauf
    - exit/quit/beenden: Beendet den Assistenten
    
    Für alle anderen Anfragen stehe ich als KI-Assistent zur Verfügung!
    """
    return help_text


def open_program(program_name):
    """Open a program on the system."""
    known_programs = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "rechner": "calc.exe",
        "taschenrechner": "calc.exe",
        "explorer": "explorer.exe",
        "browser": "explorer.exe https://www.google.de",
        "editor": "notepad.exe"
    }
    
    try:
        if program_name in known_programs:
            os.startfile(known_programs[program_name])
            return f"Das Programm '{program_name}' wird geöffnet."
        else:
            # Try to open it directly
            try:
                os.startfile(program_name)
                return f"Versuche, '{program_name}' zu öffnen."
            except:
                return f"Entschuldigung, ich konnte '{program_name}' nicht öffnen. Ist es auf deinem System installiert?"
    except Exception as e:
        logging.error(f"Error opening program {program_name}: {str(e)}")
        return f"Es gab einen Fehler beim Öffnen von '{program_name}': {str(e)}"


def open_url(url):
    """Open a URL in the default web browser."""
    if not url:
        return "Bitte gib eine URL an, die ich öffnen soll."
    
    # Add http:// if no protocol is specified
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        webbrowser.open(url)
        return f"Die URL '{url}' wurde im Browser geöffnet."
    except Exception as e:
        logging.error(f"Error opening URL {url}: {str(e)}")
        return f"Es gab einen Fehler beim Öffnen der URL '{url}': {str(e)}"


def web_search(query):
    """Perform a web search using the default search engine."""
    if not query:
        return "Bitte gib einen Suchbegriff an."
    
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    try:
        webbrowser.open(search_url)
        return f"Ich habe eine Suche nach '{query}' gestartet."
    except Exception as e:
        logging.error(f"Error performing search for {query}: {str(e)}")
        return f"Es gab einen Fehler bei der Suche nach '{query}': {str(e)}"


# GUI version if PyQt5 is available
if GUI_AVAILABLE:
    class GenerateResponseThread(QThread):
        """Thread for generating responses without blocking the UI."""
        
        response_ready = pyqtSignal(str)
        error_occurred = pyqtSignal(str)
        
        def __init__(self, response_generator, user_text, chat_history):
            super().__init__()
            self.response_generator = response_generator
            self.user_text = user_text
            self.chat_history = chat_history
        
        def run(self):
            """Generate a response in a separate thread."""
            try:
                # Add a short delay to simulate "thinking"
                time.sleep(0.5 + random.random() * 1.5)
                response = self.response_generator.generate_response(self.user_text, self.chat_history)
                self.response_ready.emit(response)
            except Exception as e:
                logging.error("Error in response generation thread:", exc_info=True)
                self.error_occurred.emit(f"Entschuldigung, ich konnte keine Antwort generieren. Fehler: {str(e)}")
    
    
    class SettingsDialog(QDialog):
        """Dialog for configuring application settings."""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Einstellungen")
            self.resize(400, 300)
            self.setup_ui()
        
        def setup_ui(self):
            """Set up the settings dialog UI."""
            layout = QVBoxLayout(self)
            
            # Create tabs
            tabs = QTabWidget()
            
            # UI settings tab
            ui_tab = QWidget()
            ui_layout = QVBoxLayout(ui_tab)
            
            # Theme selection
            theme_label = QLabel("Theme:")
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(["Dunkel", "Hell", "System"])
            ui_layout.addWidget(theme_label)
            ui_layout.addWidget(self.theme_combo)
            
            # Font size
            font_label = QLabel("Schriftgröße:")
            self.font_spin = QSpinBox()
            self.font_spin.setRange(10, 24)
            self.font_spin.setValue(16)
            ui_layout.addWidget(font_label)
            ui_layout.addWidget(self.font_spin)
            
            # Auto-response
            self.auto_response_check = QCheckBox("Automatische Antworten aktivieren")
            self.auto_response_check.setChecked(True)
            ui_layout.addWidget(self.auto_response_check)
            
            ui_layout.addStretch()
            tabs.addTab(ui_tab, "Benutzeroberfläche")
            
            # About tab
            about_tab = QWidget()
            about_layout = QVBoxLayout(about_tab)
            
            about_text = QTextEdit()
            about_text.setReadOnly(True)
            about_text.setHtml("""
            <h2>KI-Assistent Deluxe</h2>
            <p>Version 2.0</p>
            <p>Ein moderner KI-Assistent mit schönem Design und nützlichen Funktionen.</p>
            <p>Completely free of charge - keine externen APIs erforderlich.</p>
            <p>© 2023-2025 KI-Assistent Team</p>
            """)
            about_layout.addWidget(about_text)
            
            tabs.addTab(about_tab, "Über")
            
            layout.addWidget(tabs)
            
            # Buttons
            button_layout = QHBoxLayout()
            save_button = QPushButton("Speichern")
            save_button.clicked.connect(self.accept)
            cancel_button = QPushButton("Abbrechen")
            cancel_button.clicked.connect(self.reject)
            
            button_layout.addWidget(save_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
    
    
    class KI_Assistent(QMainWindow):
        """Main application window for the KI-Assistent Deluxe."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("✨ KI-Assistent Deluxe 2.0 ✨")
            self.setGeometry(200, 100, 1000, 800)
            
            # Initialize response generator
            if TRANSFORMERS_AVAILABLE:
                self.response_generator = TransformerResponseGenerator()
            else:
                self.response_generator = SimpleResponseGenerator()
            
            # Setup UI
            self.setup_ui()
            
            # Initialize chat history
            self.chat_history = []
            
            # Add initial system message
            self.add_system_message("Willkommen beim KI-Assistent Deluxe!")
            self.add_system_message("Ich bin dein persönlicher Assistent und stehe dir mit Rat und Tat zur Seite.")
            self.add_system_message("Tippe 'hilfe' um zu sehen, was ich alles kann.")
            
            # Set up automatic assistant activation
            self.activation_timer = QTimer(self)
            self.activation_timer.timeout.connect(self.activate_assistant)
            self.activation_timer.start(300000)  # Every 5 minutes
            
            # Set status
            self.status_label.setText("Status: Bereit")
        
        def setup_ui(self):
            """Set up the main application UI."""
            # Main widget and layout
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)
            self.main_layout.setSpacing(15)
            self.main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Set application font
            app_font = QFont("Segoe UI", 12)
            QApplication.setFont(app_font)
            
            # Set application style
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1E1E1E;
                }
                QWidget {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                QToolBar {
                    background-color: #252526;
                    border: none;
                    padding: 10px;
                    spacing: 15px;
                }
                QToolBar QToolButton {
                    background-color: #3A3A3A;
                    border-radius: 6px;
                    padding: 8px;
                }
                QToolBar QToolButton:hover {
                    background-color: #505050;
                }
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0086F0;
                }
                QLineEdit {
                    background-color: #252526;
                    color: #E0E0E0;
                    border: 2px solid #3A3A3A;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 16px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078D7;
                }
                QStatusBar {
                    background-color: #0078D7;
                    color: white;
                }
            """)
            
            # Header with title - Modern Copilot-like design
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 15)
            
            # Title
            title_label = QLabel("✨ KI-Assistent Deluxe ✨")
            title_label.setStyleSheet("""
                font-size: 32px;
                font-weight: bold;
                color: #0078D7;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
            title_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(title_label, 1)
            
            self.main_layout.addWidget(header_widget)
            
            # Toolbar - Modern flat design
            toolbar = QToolBar()
            toolbar.setMovable(False)
            toolbar.setIconSize(QSize(24, 24))
            toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toolbar.setStyleSheet("""
                QToolBar {
                    background-color: #252526;
                    border-radius: 8px;
                }
            """)
            
            # Clear chat action
            clear_action = QAction("Chat löschen", self)
            clear_action.triggered.connect(self.clear_chat)
            toolbar.addAction(clear_action)
            
            toolbar.addSeparator()
            
            # Settings action
            settings_action = QAction("Einstellungen", self)
            settings_action.triggered.connect(self.show_settings)
            toolbar.addAction(settings_action)
            
            # Help action
            help_action = QAction("Hilfe", self)
            help_action.triggered.connect(self.show_help)
            toolbar.addAction(help_action)
            
            self.main_layout.addWidget(toolbar)
            
            # Chat display area - Larger text and better styling
            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            self.chat_display.setStyleSheet("""
                background-color: #252526;
                color: #E0E0E0;
                font-size: 18px;
                padding: 15px;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
            """)
            self.main_layout.addWidget(self.chat_display, 1)
            
            # Input area - Modern styling
            input_widget = QWidget()
            input_layout = QHBoxLayout(input_widget)
            input_layout.setContentsMargins(0, 15, 0, 0)
            input_layout.setSpacing(15)
            
            # User input field
            self.user_input = QLineEdit()
            self.user_input.setPlaceholderText("Schreibe hier deine Nachricht...")
            self.user_input.setStyleSheet("""
                background-color: #252526;
                color: #E0E0E0;
                font-size: 18px;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #3A3A3A;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
            self.user_input.setMinimumHeight(50)
            self.user_input.returnPressed.connect(self.send_message)
            input_layout.addWidget(self.user_input, 1)
            
            # Send button - Modern blue button
            self.send_button = QPushButton("Senden")
            self.send_button.setStyleSheet("""
                background-color: #0078D7;
                color: white;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
            self.send_button.setMinimumHeight(50)
            self.send_button.clicked.connect(self.send_message)
            input_layout.addWidget(self.send_button)
            
            self.main_layout.addWidget(input_widget)
            
            # Status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            
            # Add status label
            self.status_label = QLabel("Status: Initialisierung...")
            self.status_bar.addPermanentWidget(self.status_label)
        
        def send_message(self):
            """Process user input and send a message."""
            user_text = self.user_input.text().strip()
            if not user_text:
                return
            
            # Add the user message to the chat
            self.add_user_message(user_text)
            
            # Handle commands
            command, args = parse_command(user_text)
            if command:
                self.handle_command(command, args)
            else:
                # Show thinking indicator
                self.add_system_message("Ich denke nach...", temp=True)
                
                # Generate response in a separate thread
                self.response_thread = GenerateResponseThread(
                    self.response_generator, user_text, self.chat_history
                )
                self.response_thread.response_ready.connect(self.on_response_ready)
                self.response_thread.error_occurred.connect(self.on_response_error)
                self.response_thread.start()
            
            # Clear the input field
            self.user_input.clear()
        
        def handle_command(self, command, args):
            """Handle various commands from user input."""
            if command == "open_program":
                response = open_program(args)
                self.add_assistant_message(response)
            elif command == "open_url":
                response = open_url(args)
                self.add_assistant_message(response)
            elif command == "search":
                response = web_search(args)
                self.add_assistant_message(response)
            elif command == "help":
                self.show_help()
            elif command == "clear_chat":
                self.clear_chat()
                self.add_system_message("Der Chat wurde gelöscht.")
            elif command == "exit":
                self.close()
        
        def on_response_ready(self, response):
            """Handle response when it's ready from the generator."""
            # Remove the "thinking" message if it exists
            self.remove_temp_messages()
            
            # Add the assistant response to the chat
            self.add_assistant_message(response)
        
        def on_response_error(self, error_message):
            """Handle error during response generation."""
            # Remove the "thinking" message if it exists
            self.remove_temp_messages()
            
            # Add the error message to the chat
            self.add_system_message(f"Fehler: {error_message}")
        
        def add_user_message(self, message):
            """Add a user message to the chat display."""
            formatted = f"Du: {message}"
            self.chat_history.append(formatted)
            
            # Create styled message with modern Copilot-like styling
            self.chat_display.append(f'''
                <div style="
                    margin: 15px 5px; 
                    display: block; 
                    text-align: right;
                ">
                    <div style="
                        display: inline-block; 
                        background-color: #0078D7; 
                        color: #FFFFFF; 
                        border-radius: 18px; 
                        padding: 15px 20px; 
                        max-width: 85%; 
                        text-align: left;
                        font-size: 18px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    ">
                        {formatted}
                    </div>
                </div>
            ''')
            self.scroll_to_bottom()
        
        def add_assistant_message(self, message):
            """Add an assistant message to the chat display."""
            formatted = f"Assistent: {message}"
            self.chat_history.append(formatted)
            
            # Create styled message with modern Copilot-like styling
            self.chat_display.append(f'''
                <div style="
                    margin: 15px 5px; 
                    display: block;
                ">
                    <div style="
                        display: inline-block; 
                        background-color: #252526; 
                        color: #FFFFFF; 
                        border-radius: 18px; 
                        padding: 15px 20px; 
                        max-width: 85%; 
                        border-left: 4px solid #0078D7;
                        font-size: 18px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    ">
                        {formatted}
                    </div>
                </div>
            ''')
            self.scroll_to_bottom()
        
        def add_system_message(self, message, temp=False):
            """Add a system message to the chat display."""
            # System messages are not added to chat history
            
            # Create styled message with a system indicator and modern styling
            temp_class = 'class="temp-message"' if temp else ''
            self.chat_display.append(f'''
                <div {temp_class} style="
                    margin: 10px auto;
                    text-align: center;
                ">
                    <div style="
                        display: inline-block;
                        background-color: #2D2D30;
                        color: #A0A0A0;
                        border-radius: 15px;
                        padding: 8px 15px;
                        font-style: italic;
                        font-size: 16px;
                        max-width: 80%;
                    ">
                        System: {message}
                    </div>
                </div>
            ''')
            self.scroll_to_bottom()
        
        def remove_temp_messages(self):
            """Remove temporary messages from the display."""
            # Get current HTML
            html = self.chat_display.toHtml()
            
            # Remove divs with class="temp-message"
            html = re.sub(r'<div[^>]*class="temp-message"[^>]*>.*?</div>', '', html, flags=re.DOTALL)
            
            # Set the modified HTML back
            self.chat_display.setHtml(html)
            self.scroll_to_bottom()
        
        def scroll_to_bottom(self):
            """Scroll chat display to the bottom to show latest messages."""
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_display.setTextCursor(cursor)
        
        def show_help(self):
            """Show help information."""
            self.add_system_message(get_help_text())
        
        def clear_chat(self):
            """Clear the chat history and display."""
            self.chat_history = []
            self.chat_display.clear()
            self.add_system_message("Chat gelöscht. Wie kann ich dir helfen?")
        
        def show_settings(self):
            """Show the settings dialog."""
            dialog = SettingsDialog(self)
            if dialog.exec_():
                self.apply_settings(dialog)
        
        def apply_settings(self, dialog):
            """Apply settings from the settings dialog."""
            # Apply theme
            theme = dialog.theme_combo.currentText()
            if theme == "Hell":
                # Light theme settings
                self.setStyleSheet("")  # Reset
                self.chat_display.setStyleSheet("background-color: white; color: black;")
                self.user_input.setStyleSheet("background-color: #f0f0f0; color: black; border: 1px solid #cccccc;")
            else:
                # Dark theme
                self.setStyleSheet("background-color: #263238; color: #FFFFFF;")
                self.chat_display.setStyleSheet("background-color: #37474F; color: #FFFFFF; font-size: 16px; padding: 12px;")
                self.user_input.setStyleSheet("background-color: #455A64; color: #FFFFFF; font-size: 16px; padding: 12px;")
            
            # Apply font size
            font_size = dialog.font_spin.value()
            current_font = self.chat_display.font()
            current_font.setPointSize(font_size)
            self.chat_display.setFont(current_font)
            self.user_input.setFont(current_font)
            
            # Apply auto-response setting
            if dialog.auto_response_check.isChecked():
                if not self.activation_timer.isActive():
                    self.activation_timer.start(300000)
            else:
                if self.activation_timer.isActive():
                    self.activation_timer.stop()
        
        def activate_assistant(self):
            """Automatically activate the assistant periodically."""
            messages = [
                "Brauchst du Hilfe bei etwas?",
                "Wie kann ich dir behilflich sein?",
                "Gibt es etwas, womit ich dir helfen kann?",
                "Ich bin hier, wenn du Fragen hast.",
                "Benötigst du Unterstützung bei einer Aufgabe?"
            ]
            self.add_assistant_message(random.choice(messages))


# CLI version for systems without PyQt5
def cli_main():
    """Main function to run the CLI assistant."""
    # Print welcome message with ASCII art
    print(ASCII_LOGO)
    print("\n" + "=" * 80)
    print("✨  KI-Assistent Deluxe - CLI Version  ✨".center(80))
    print("=" * 80 + "\n")
    
    print("Willkommen beim KI-Assistent Deluxe!")
    print("Ich bin dein persönlicher Assistent und stehe dir mit Rat und Tat zur Seite.")
    print("Tippe 'hilfe' um zu sehen, was ich alles kann.")
    print("Zum Beenden tippe 'exit', 'quit' oder 'beenden'.\n")
    
    # Initialize the appropriate response generator
    if TRANSFORMERS_AVAILABLE:
        print("Lade KI-Modell, bitte warten...")
        response_generator = TransformerResponseGenerator()
        if response_generator.is_model_loaded():
            print("KI-Modell erfolgreich geladen!\n")
        else:
            print("Konnte KI-Modell nicht laden, verwende einfache Antworten.\n")
            response_generator = SimpleResponseGenerator()
    else:
        response_generator = SimpleResponseGenerator()
    
    # Initialize chat history
    chat_history = deque(maxlen=20)  # Only keep the last 20 messages
    
    # Main interaction loop
    while True:
        # Get user input
        user_text = input("Du: ").strip()
        
        # Handle empty input
        if not user_text:
            continue
        
        # Add user input to chat history
        chat_history.append(f"Du: {user_text}")
        
        # Parse commands
        command, args = parse_command(user_text)
        
        # Handle commands
        if command == "exit":
            print("\nAuf Wiedersehen! Bis zum nächsten Mal.")
            break
        elif command == "help":
            print("\n" + get_help_text())
        elif command == "clear_chat":
            chat_history.clear()
            print("\nDer Chat wurde gelöscht.")
            os.system('cls' if os.name == 'nt' else 'clear')
            print(ASCII_LOGO)
            print("\n" + "=" * 80)
            print("✨  KI-Assistent Deluxe - CLI Version  ✨".center(80))
            print("=" * 80 + "\n")
        elif command == "open_program":
            response = open_program(args)
            print(f"Assistent: {response}")
            chat_history.append(f"Assistent: {response}")
        elif command == "open_url":
            response = open_url(args)
            print(f"Assistent: {response}")
            chat_history.append(f"Assistent: {response}")
        elif command == "search":
            response = web_search(args)
            print(f"Assistent: {response}")
            chat_history.append(f"Assistent: {response}")
        else:
            # Generate a response
            print("Assistent: Ich denke nach...")
            
            # Use a separate thread for generating responses to keep the CLI responsive
            def generate_in_thread():
                # Simulate thinking time
                time.sleep(0.5 + random.random() * 1.5)
                response = response_generator.generate_response(user_text, list(chat_history))
                print(f"Assistent: {response}")
                chat_history.append(f"Assistent: {response}")
            
            # Start thread and wait for it to complete
            thread = threading.Thread(target=generate_in_thread)
            thread.start()
            thread.join()
        
        print()  # Add an empty line for better readability


# Main entry point
if __name__ == "__main__":
    try:
        if GUI_AVAILABLE:
            # Start the GUI version
            app = QApplication(sys.argv)
            window = KI_Assistent()
            window.show()
            sys.exit(app.exec_())
        else:
            # Start the CLI version
            cli_main()
    except KeyboardInterrupt:
        print("\n\nAssistent: Auf Wiedersehen! Das Programm wurde beendet.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\nEs ist ein unerwarteter Fehler aufgetreten: {str(e)}")
        print("Details wurden in der Logdatei gespeichert.")