import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Meter

class QuizView:
    def __init__(self, root):
        self.root = root
        self.style = Style(theme="flatly")
        self.root.title("Quiz App")
        self.root.geometry("900x700")

        self.style.configure("TRadiobutton", font=("Arial", 12))
        self.style.configure("TCheckbutton", font=("Arial", 12))

        self.main_frame = None
        self.current_screen = None
        self.start_button = None
        self.submit_button = None
        self.restart_button = None
        self.exit_button = None

    def create_menu(self, restart_callback, quit_callback, about_callback):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Fichier", menu=self.file_menu)
        self.file_menu.add_command(label="Redémarrer le quiz", command=restart_callback)
        self.file_menu.add_command(label="Quitter", command=quit_callback)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Aide", menu=self.help_menu)
        self.help_menu.add_command(label="A propos", command=about_callback)

    def clear_widgets(self):
        if self.main_frame:
            self.main_frame.destroy()
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

    def show_start_menu(self):
        self.clear_widgets()
        self.current_screen = "start_menu"

        self.title_label = ttk.Label(self.main_frame, text="Bienvenue sur Quizz CCNA1!", font=("Helvetica", 26, "bold"))
        self.title_label.pack(pady=20)

        self.num_questions_label = ttk.Label(self.main_frame, text="Nombre de questions (60 au CCNA1):")
        self.num_questions_label.pack(pady=10)

        self.num_questions_entry = ttk.Entry(self.main_frame, width=10)
        self.num_questions_entry.pack(pady=10)
        self.num_questions_entry.focus()

        self.start_button = ttk.Button(self.main_frame, text="Démarrer le quiz", style='success.TButton')
        self.start_button.pack(pady=20)

        return self.start_button

    def show_question(self, question, current_question, total_questions):
        self.clear_widgets()
        self.current_screen = "question"

        self.question_label = ttk.Label(self.main_frame, text=question['question'], wraplength=600, font=("Helvetica", 16))
        self.question_label.pack(pady=20)

        self.answer_vars = []
        self.answer_widgets = []
        
        answers = question.get('answers', [])
        
        if not answers:
            self.show_error("No answers found for this question.")
            return

        correct_answers_count = sum(1 for answer in answers if answer.get('correct-answer', False))

        if correct_answers_count == 1:
            var = tk.IntVar(value=-1)
            self.answer_vars.append(var)
            for i, answer in enumerate(answers, start=1):
                rb = ttk.Radiobutton(self.main_frame, text=f"{i}. {answer['text']}", variable=var, value=i-1)
                rb.pack(anchor='w', padx=20, pady=5)
                self.answer_widgets.append(rb)
        else:
            for i, answer in enumerate(answers, start=1):
                var = tk.BooleanVar()
                self.answer_vars.append(var)
                cb = ttk.Checkbutton(self.main_frame, text=f"{i}. {answer['text']}", variable=var)
                cb.pack(anchor='w', padx=20, pady=5)
                self.answer_widgets.append(cb)

        self.submit_button = ttk.Button(self.main_frame, text="Soumettre", style='success.TButton')
        self.submit_button.pack(pady=20)

        self.progress_label = ttk.Label(self.main_frame, text=f"Question {current_question} sur {total_questions}")
        self.progress_label.pack(side="bottom", pady=10)

        self.timer_label = ttk.Label(self.main_frame, text="Temps écoulé: 00:00")
        self.timer_label.pack(side="bottom", pady=5)

    def update_timer(self, elapsed_time):
        minutes, seconds = divmod(elapsed_time, 60)
        self.timer_label.config(text=f"Temps écoulé: {minutes:02d}:{seconds:02d}")

    def show_results(self, score, total, score_percentage, elapsed_time, user_answers, selected_questions):
        self.clear_widgets()
        self.current_screen = "results"

        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        self.result_label = ttk.Label(header_frame, text="Fin du Quiz !", font=("Helvetica", 26, "bold"))
        self.result_label.pack(side="left")

        score_label = ttk.Label(header_frame, text=f"Score : {score}/{total} ", font=("Helvetica", 18))
        score_label.pack(side="right")

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

        for index, answer in enumerate(user_answers):
            question_frame = ttk.Frame(self.scrollable_frame)
            question_frame.pack(pady=10, fill='x', expand=True)

            question_number = ttk.Label(question_frame, text=f"Question {index + 1}", font=("Helvetica", 16, "bold"))
            question_number.pack(anchor='w')

            question_text = ttk.Label(question_frame, text=answer['question'], wraplength=800, font=("Helvetica", 12))
            question_text.pack(anchor='w', padx=(20, 0), pady=5)

            for i, option in enumerate(selected_questions[index]['answers'], start=1):
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

        self.restart_button = ttk.Button(button_frame, text="Recommencer", style='success.TButton')
        self.restart_button.pack(side="left", padx=10)

        self.exit_button = ttk.Button(button_frame, text="Quitter", style='danger.TButton')
        self.exit_button.pack(side="left", padx=10)

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    def on_mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def show_error(self, message):
        messagebox.showerror("Erreur", message)

    def show_about(self):
        messagebox.showinfo("À Propos", "\nVersion 1.0\n\nCréé par Jules Rachet")
