import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from ttkbootstrap import Style
from ttkbootstrap.widgets import Meter
import time

class QuizApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.current_question_index = 0
        self.user_answers = []
        self.num_questions = 0
        self.selected_questions = []
        self.answer_vars = []
        self.start_time = None
        self.timer_id = None

        self.style = Style(theme="flatly")  # Choisir un thème moderne
        self.root.title("Quiz App")
        self.root.geometry("900x700")

        self.style.configure("TRadiobutton", font=("Arial", 12))
        self.style.configure("TCheckbutton", font=("Arial", 12))

        self.create_menu()
        self.start_menu()

        self.root.bind('<Return>', self.handle_enter)
        self.root.bind('<KP_Enter>', self.handle_enter)
        self.root.bind('r', self.handle_restart)

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Fichier", menu=self.file_menu)
        self.file_menu.add_command(label="Redémarrer le quiz", command=self.restart_quiz)
        self.file_menu.add_command(label="Quitter", command=self.root.quit)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Aide", menu=self.help_menu)
        self.help_menu.add_command(label="A propos", command=self.show_about)

    def start_menu(self):
        self.clear_widgets()
        self.current_screen = "start_menu"

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        self.title_label = ttk.Label(self.main_frame, text="Bienvenue sur Quizz CCNA1!", font=("Helvetica", 26, "bold"))
        self.title_label.pack(pady=20)

        self.num_questions_label = ttk.Label(self.main_frame, text="Nombre de questions (60 au CCNA1):")
        self.num_questions_label.pack(pady=10)

        self.num_questions_entry = ttk.Entry(self.main_frame, width=10)
        self.num_questions_entry.pack(pady=10)
        self.num_questions_entry.focus()

        self.start_button = ttk.Button(self.main_frame, text="Démarrer le quiz", command=self.start_quiz, style='success.TButton')
        self.start_button.pack(pady=20)

    def start_quiz(self):
        try:
            self.num_questions = int(self.num_questions_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Entrez un nombre valide de questions.")
            return

        if self.num_questions <= 0 or self.num_questions > len(self.data):
            messagebox.showerror("Erreur", f"Entrez un nombre entre 1 et {len(self.data)}.")
            return

        self.selected_questions = random.sample(self.data, self.num_questions)
        self.current_question_index = 0
        self.user_answers = []
        self.start_time = time.time()
        self.show_question()

    def show_question(self):
        self.clear_widgets()
        self.current_screen = "question"
    
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        question = self.selected_questions[self.current_question_index]
    
        # Affiche la question
        self.question_label = ttk.Label(self.main_frame, text=question['question'], wraplength=600, font=("Helvetica", 16))
        self.question_label.pack(pady=20)
    
        # Mélange les réponses
        shuffled_answers = question['answers'].copy()
        random.shuffle(shuffled_answers)
    
        # Détermine si la question a plusieurs réponses correctes
        self.answer_vars = []
        correct_answers_count = sum(1 for answer in shuffled_answers if answer.get('correct-answer', False))
    
        if correct_answers_count == 1:  # Si une seule réponse correcte, utiliser Radiobuttons
            var = tk.IntVar(value=-1)
            self.answer_vars.append(var)
            for i, answer in enumerate(shuffled_answers, start=1):
                rb = ttk.Radiobutton(self.main_frame, text=f"{i}. {answer['text']}", variable=var, value=i-1)
                rb.pack(anchor='w', padx=20, pady=5)
        else:  # Si plusieurs réponses correctes, utiliser Checkbuttons
            for i, answer in enumerate(shuffled_answers, start=1):
                var = tk.BooleanVar()
                self.answer_vars.append(var)
                cb = ttk.Checkbutton(self.main_frame, text=f"{i}. {answer['text']}", variable=var)
                cb.pack(anchor='w', padx=20, pady=5)
    
        # Bind des touches numériques pour sélectionner les réponses
        for i in range(1, len(shuffled_answers) + 1):
            self.root.bind(str(i), lambda e, i=i: self.toggle_answer(i-1))
            self.root.bind(f"<KP_{i}>", lambda e, i=i: self.toggle_answer(i-1))
    
        # Bouton pour soumettre la réponse
        self.submit_button = ttk.Button(self.main_frame, text="Soumettre", command=self.submit_answer, style='success.TButton')
        self.submit_button.pack(pady=20)
    
        # Affichage de la progression
        self.progress_label = ttk.Label(self.main_frame, text=f"Question {self.current_question_index + 1} sur {self.num_questions}")
        self.progress_label.pack(side="bottom", pady=10)

        # Affichage du timer
        self.timer_label = ttk.Label(self.main_frame, text="Temps écoulé: 00:00")
        self.timer_label.pack(side="bottom", pady=5)
        self.update_timer()

        # Stocke les réponses mélangées pour une utilisation ultérieure
        question['shuffled_answers'] = shuffled_answers

    def update_timer(self):
        if self.start_time is not None:
            elapsed_time = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            self.timer_label.config(text=f"Temps écoulé: {minutes:02d}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)

    def toggle_answer(self, index):
        if isinstance(self.answer_vars[0], tk.IntVar):
            self.answer_vars[0].set(index)
        else:
            current_value = self.answer_vars[index].get()
            self.answer_vars[index].set(not current_value)

    def submit_answer(self):
        question = self.selected_questions[self.current_question_index]
        user_answer_indices = []

        if isinstance(self.answer_vars[0], tk.IntVar):
            selected_index = self.answer_vars[0].get()
            if selected_index >= 0:
                user_answer_indices.append(selected_index)
        else:
            for i, var in enumerate(self.answer_vars):
                if var.get():
                    user_answer_indices.append(i)

        if not user_answer_indices:
            messagebox.showerror("Erreur", "Sélectionnez au moins une réponse.")
            return

        correct_answer_indices = [i for i, answer in enumerate(question['shuffled_answers']) if answer.get('correct-answer', False)]
        is_correct = set(user_answer_indices) == set(correct_answer_indices)

        self.user_answers.append({
            'question': question['question'],
            'user_answers': [question['shuffled_answers'][i]['text'] for i in user_answer_indices],
            'is_correct': is_correct
        })

        self.current_question_index += 1
        if self.current_question_index < self.num_questions:
            self.show_question()
        else:
            self.show_results()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

    def show_results(self):
        self.clear_widgets()
        self.current_screen = "results"

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        score_percentage = round(self.calculate_score(), 2)
        score = sum(1 for answer in self.user_answers if answer['is_correct'])
        total = len(self.user_answers)

        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        self.result_label = ttk.Label(header_frame, text="Fin du Quiz !", font=("Helvetica", 26, "bold"))
        self.result_label.pack(side="left")

        score_label = ttk.Label(header_frame, text=f"Score : {score}/{total} ", font=("Helvetica", 18))
        score_label.pack(side="right")

        # Affichage du temps total
        elapsed_time = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed_time, 60)
        time_label = ttk.Label(header_frame, text=f"Temps total: {minutes:02d}:{seconds:02d}", font=("Helvetica", 18))
        time_label.pack(side="right", padx=20)

        meter = Meter(self.main_frame, amountused=score_percentage, metersize=200, padding=20,
                      subtext="Taux de Réussite", textfont=("Helvetica", 16), subtextfont=("Helvetica", 12),
                      textright="%", bootstyle="success")
        meter.pack(pady=10)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar_y = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        for index, answer in enumerate(self.user_answers):
            question_frame = ttk.Frame(self.scrollable_frame)
            question_frame.pack(pady=10, fill='x', expand=True)

            question_number = ttk.Label(question_frame, text=f"Question {index + 1}", font=("Helvetica", 16, "bold"))
            question_number.pack(anchor='w')

            question_text = ttk.Label(question_frame, text=answer['question'], wraplength=800, font=("Helvetica", 12))
            question_text.pack(anchor='w', padx=(20, 0), pady=5)

            for i, option in enumerate(self.selected_questions[index]['shuffled_answers'], start=1):
                text = option['text']
                is_correct = option.get('correct-answer', False)
                is_user_answer = text in answer['user_answers']

                if is_user_answer and is_correct:
                    label = ttk.Label(question_frame, text=f"{i}. ✓ {text}", font=("Helvetica", 12, "bold"), foreground="green")
                elif is_user_answer and not is_correct:
                    label = ttk.Label(question_frame, text=f"{i}. ✗ {text}", font=("Helvetica", 12, "italic"), foreground="red")
                elif is_correct:
                    label = ttk.Label(question_frame, text=f"{i}. • {text}", font=("Helvetica", 12), foreground="green")
                else:
                    label = ttk.Label(question_frame, text=f"{i}. {text}", font=("Helvetica", 12))

                label.pack(anchor='w', padx=(20, 0), pady=2)

            ttk.Separator(question_frame, orient='horizontal').pack(fill='x', pady=10)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        self.restart_button = ttk.Button(button_frame, text="Recommencer", command=self.restart_quiz, style='success.TButton')
        self.restart_button.pack(side="left", padx=10)

        self.exit_button = ttk.Button(button_frame, text="Quitter", command=self.root.quit, style='danger.TButton')
        self.exit_button.pack(side="left", padx=10)

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    def on_mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def restart_quiz(self):
        self.start_time = None
        self.start_menu()

    def handle_enter(self, event):
        if self.current_screen == "start_menu":
            self.start_quiz()
        elif self.current_screen == "question":
            self.submit_answer()
        elif self.current_screen == "results":
            self.restart_quiz()

    def handle_restart(self, event):
        if self.current_screen == "results":
            self.restart_quiz()

    def show_about(self):
        messagebox.showinfo("À Propos", "\nVersion 1.0\n\nCréé par Jules Rachet")

    def calculate_score(self):
        correct_answers = sum(answer['is_correct'] for answer in self.user_answers)
        return (correct_answers / len(self.user_answers)) * 100

def load_questions(filename):
    with open(filename, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    root = tk.Tk()
    data = load_questions("questions.json")
    app = QuizApp(root, data)
    root.mainloop()
