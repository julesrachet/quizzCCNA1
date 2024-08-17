import tkinter as tk
from model import QuizModel
from view import QuizView
from controller import QuizController

if __name__ == "__main__":
    root = tk.Tk()
    model = QuizModel("questions.json")
    view = QuizView(root)
    controller = QuizController(model, view)
    root.mainloop()
