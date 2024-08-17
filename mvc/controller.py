import time
import random
import tkinter as tk

class QuizController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.start_time = 0
        self.elapsed_time = 0

        self.start_button = self.view.show_start_menu()
        self.start_button.config(command=self.start_quiz)
        self.view.create_menu(self.restart_quiz, self.quit_quiz, self.view.show_about)

        self.view.root.bind('<Return>', self.handle_return)
        self.view.root.bind('<KP_Enter>', self.handle_return)
        self.view.root.bind('r', self.handle_r)
        self.view.root.bind('R', self.handle_r)

    def start_quiz(self):
        num_questions = int(self.view.num_questions_entry.get())
        self.questions = self.model.get_questions(num_questions)
        random.shuffle(self.questions)
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.start_time = time.time()
        self.show_question()

    def show_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Shuffle the answers
            shuffled_answers = question['answers'].copy()
            random.shuffle(shuffled_answers)
            question['answers'] = shuffled_answers

            self.view.show_question(question, self.current_question + 1, len(self.questions))
            self.view.submit_button.config(command=self.check_answer)
            self.update_timer()

            # Bind number keys
            for i in range(1, min(8, len(question['answers']) + 1)):
                self.view.root.bind(str(i), lambda event, index=i-1: self.toggle_answer(index))
                self.view.root.bind(f'<KP_{i}>', lambda event, index=i-1: self.toggle_answer(index))

        else:
            self.show_results()

    def toggle_answer(self, index):
        if isinstance(self.view.answer_vars[0], tk.IntVar):  # Single choice
            self.view.answer_vars[0].set(index)
        else:  # Multiple choice
            current_value = self.view.answer_vars[index].get()
            self.view.answer_vars[index].set(not current_value)

    def check_answer(self):
        question = self.questions[self.current_question]
        user_answer = []
        correct_answers = [answer['text'] for answer in question['answers'] if answer.get('correct-answer', False)]

        if len(correct_answers) == 1:  # Single answer question
            selected = self.view.answer_vars[0].get()
            if selected != -1:
                user_answer = [question['answers'][selected]['text']]
        else:  # Multiple answer question
            for i, var in enumerate(self.view.answer_vars):
                if var.get():
                    user_answer.append(question['answers'][i]['text'])

        is_correct = set(user_answer) == set(correct_answers)
        if is_correct:
            self.score += 1

        self.user_answers.append({
            'question': question['question'],
            'user_answers': user_answer,
            'correct_answers': correct_answers,
            'is_correct': is_correct
        })

        self.current_question += 1
        self.show_question()

    def show_results(self):
        self.elapsed_time = int(time.time() - self.start_time)
        score_percentage = (self.score / len(self.questions)) * 100
        self.view.show_results(self.score, len(self.questions), score_percentage, 
                               self.elapsed_time, self.user_answers, self.questions)
        self.view.restart_button.config(command=self.restart_quiz)
        self.view.exit_button.config(command=self.quit_quiz)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.view.update_timer(elapsed)
        if self.current_question < len(self.questions):
            self.view.root.after(1000, self.update_timer)

    def restart_quiz(self):
        self.start_button = self.view.show_start_menu()
        self.start_button.config(command=self.start_quiz)

    def quit_quiz(self):
        self.view.root.quit()

    def handle_return(self, event):
        if self.view.current_screen == "start_menu":
            self.start_quiz()
        elif self.view.current_screen == "question":
            self.check_answer()

    def handle_r(self, event):
        if self.view.current_screen == "results":
            self.restart_quiz()
