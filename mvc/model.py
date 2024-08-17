import json
import random
import time

class QuizModel:
    def __init__(self, filename):
        self.data = self.load_questions(filename)
        self.num_questions = 0
        self.selected_questions = []
        self.current_question_index = 0
        self.user_answers = []
        self.start_time = None

    def load_questions(self, filename):
        with open(filename, 'r') as file:
            return json.load(file)

    def start_quiz(self, num_questions):
        self.num_questions = num_questions
        self.selected_questions = random.sample(self.data, self.num_questions)
        self.current_question_index = 0
        self.user_answers = []
        self.start_time = time.time()

    def get_current_question(self):
        return self.selected_questions[self.current_question_index]

    def submit_answer(self, user_answer_indices):
        question = self.get_current_question()
        correct_answer_indices = [i for i, answer in enumerate(question['answers']) if answer.get('correct-answer', False)]
        is_correct = set(user_answer_indices) == set(correct_answer_indices)

        self.user_answers.append({
            'question': question['question'],
            'user_answers': [question['answers'][i]['text'] for i in user_answer_indices],
            'is_correct': is_correct
        })

        self.current_question_index += 1

    def is_quiz_finished(self):
        return self.current_question_index >= self.num_questions

    def get_results(self):
        score = sum(1 for answer in self.user_answers if answer['is_correct'])
        total = len(self.user_answers)
        score_percentage = round((score / total) * 100, 2)
        elapsed_time = int(time.time() - self.start_time)
        return score, total, score_percentage, elapsed_time

    def get_all_answers(self):
        return self.user_answers

    def get_questions(self, num_questions):
        return random.sample(self.data, num_questions)
