import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from ttkbootstrap import Style

class QuizApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.current_question_index = 0
        self.user_answers = []
        self.num_questions = 0
        self.selected_questions = []
        self.answer_vars = []

        self.style = Style(theme="flatly")
        self.root.title("Quiz App")
        self.root.geometry("900x700")

        self.create_menu()
        self.start_menu()

        self.root.bind('<Return>', self.handle_enter)
        self.root.bind('<KP_Enter>', self.handle_enter)
        self.root.bind('r', self.handle_restart)

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

    def start_menu(self):
        self.clear_widgets()
        self.current_screen = "start_menu"

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        self.title_label = ttk.Label(self.main_frame, text="Welcome to the Quiz App!", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=20)

        self.num_questions_label = ttk.Label(self.main_frame, text="Number of questions:")
        self.num_questions_label.pack(pady=10)

        self.num_questions_entry = ttk.Entry(self.main_frame, width=10)
        self.num_questions_entry.pack(pady=10)
        self.num_questions_entry.focus()

        self.start_button = ttk.Button(self.main_frame, text="Start Quiz", command=self.start_quiz, style='primary.TButton')
        self.start_button.pack(pady=20)

    def start_quiz(self):
        try:
            self.num_questions = int(self.num_questions_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of questions.")
            return

        if self.num_questions <= 0 or self.num_questions > len(self.data):
            messagebox.showerror("Error", f"Please enter a number between 1 and {len(self.data)}.")
            return

        self.selected_questions = random.sample(self.data, self.num_questions)
        self.current_question_index = 0
        self.user_answers = []
        self.show_question()

    def show_question(self):
        self.clear_widgets()
        self.current_screen = "question"

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        question = self.selected_questions[self.current_question_index]

        self.question_label = ttk.Label(self.main_frame, text=question['question'], wraplength=600, font=("Arial", 14))
        self.question_label.pack(pady=20)

        self.answer_vars = []
        is_single_answer = question.get('correct-answer-count', 1) == 1

        if is_single_answer:
            var = tk.IntVar(value=-1)
            self.answer_vars.append(var)
            for i, answer in enumerate(question['answers'], start=1):
                rb = ttk.Radiobutton(self.main_frame, text=f"{i}. {answer['text']}", variable=var, value=i-1)
                rb.pack(anchor='w', padx=20, pady=5)
        else:
            for i, answer in enumerate(question['answers'], start=1):
                var = tk.BooleanVar()
                self.answer_vars.append(var)
                cb = ttk.Checkbutton(self.main_frame, text=f"{i}. {answer['text']}", variable=var)
                cb.pack(anchor='w', padx=20, pady=5)

        for i in range(1, len(question['answers']) + 1):
            self.root.bind(str(i), lambda e, i=i: self.toggle_answer(i-1))
            self.root.bind(f"<KP_{i}>", lambda e, i=i: self.toggle_answer(i-1))

        self.submit_button = ttk.Button(self.main_frame, text="Submit", command=self.submit_answer, style='primary.TButton')
        self.submit_button.pack(pady=20)

        self.progress_label = ttk.Label(self.main_frame, text=f"Question {self.current_question_index + 1} of {self.num_questions}")
        self.progress_label.pack(side="bottom", pady=10)

    def toggle_answer(self, index):
        question = self.selected_questions[self.current_question_index]
        is_single_answer = question.get('correct-answer-count', 1) == 1

        if is_single_answer:
            self.answer_vars[0].set(index)
        else:
            if index < len(self.answer_vars):
                self.answer_vars[index].set(not self.answer_vars[index].get())

    def submit_answer(self):
        question = self.selected_questions[self.current_question_index]
        is_single_answer = question.get('correct-answer-count', 1) == 1

        if is_single_answer:
            selected_index = self.answer_vars[0].get()
            user_answers = [question['answers'][selected_index]['text']] if selected_index != -1 else []
        else:
            user_answers = [answer['text'] for answer, var in zip(question['answers'], self.answer_vars) if var.get()]

        correct_answers = [answer['text'] for answer in question['answers'] if answer.get('correct-answer', False)]
        
        is_correct = set(user_answers) == set(correct_answers)
        self.user_answers.append({
            'question': question['question'],
            'user_answers': user_answers,
            'correct_answers': correct_answers,
            'is_correct': is_correct
        })

        self.current_question_index += 1
        if self.current_question_index < self.num_questions:
            self.show_question()
        else:
            self.show_results()

    def calculate_score(self):
        correct_count = sum(1 for answer in self.user_answers if answer['is_correct'])
        return (correct_count / self.num_questions) * 100

    def show_results(self):
        self.clear_widgets()
        self.current_screen = "results"

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        score_percentage = self.calculate_score()
        score = sum(1 for answer in self.user_answers if answer['is_correct'])
        total = len(self.user_answers)

        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        self.result_label = ttk.Label(header_frame, text="Quiz Completed!", font=("Arial", 24, "bold"))
        self.result_label.pack(side="left")

        score_label = ttk.Label(header_frame, text=f"Score: {score}/{total} ({score_percentage:.1f}%)", font=("Arial", 18))
        score_label.pack(side="right")

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        for index, answer in enumerate(self.user_answers):
            question_frame = ttk.Frame(self.scrollable_frame)
            question_frame.pack(pady=10, fill='x', expand=True)

            question_number = ttk.Label(question_frame, text=f"Question {index + 1}", font=("Arial", 16, "bold"))
            question_number.pack(anchor='w')

            question_text = ttk.Label(question_frame, text=answer['question'], wraplength=800, font=("Arial", 12))
            question_text.pack(anchor='w', pady=(5, 10))

            for i, option in enumerate(self.selected_questions[index]['answers'], start=1):
                text = option['text']
                is_correct = option.get('correct-answer', False)
                is_user_answer = text in answer['user_answers']

                if is_user_answer and is_correct:
                    label = ttk.Label(question_frame, text=f"{i}. ✓ {text}", font=("Arial", 12, "bold"), foreground="green")
                elif is_user_answer and not is_correct:
                    label = ttk.Label(question_frame, text=f"{i}. ✗ {text}", font=("Arial", 12, "bold"), foreground="red")
                elif is_correct:
                    label = ttk.Label(question_frame, text=f"{i}. • {text}", font=("Arial", 12), foreground="green")
                else:
                    label = ttk.Label(question_frame, text=f"{i}. {text}", font=("Arial", 12))
                
                label.pack(anchor='w', padx=(20, 0), pady=2)

            ttk.Separator(question_frame, orient='horizontal').pack(fill='x', pady=10)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        self.restart_button = ttk.Button(button_frame, text="Restart Quiz", command=self.restart_quiz, style='primary.TButton')
        self.restart_button.pack(side="left", padx=10)

        self.exit_button = ttk.Button(button_frame, text="Exit Quiz", command=self.root.quit, style='secondary.TButton')
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
        self.start_menu()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_menu()

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
        messagebox.showinfo("About", "Quiz App\nVersion 1.0\n\nCreated by Your Name")

def load_questions(filename):
    with open(filename, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    root = tk.Tk()
    data = load_questions("updated_parsed_data.json")
    app = QuizApp(root, data)
    root.mainloop()
