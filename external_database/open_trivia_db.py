import json
import html
import sqlite3
import requests
from time import sleep

from .database_manager import DatabaseManager

class TriviaSQLiteManager(DatabaseManager):        
    def get_categories(self):
        res = requests.get("https://opentdb.com/api_category.php")
        return res.json()['trivia_categories'] if res.status_code == 200 else []
    
    def fetch_all_questions(self):
        categories = self.get_categories()
        for cat in categories:
            print(f"📚 Catégorie : {cat['name']}")
            amounts = [50, 20, 10, 5, 1]
            amout_idx = 0

            while True:
                url = f"https://opentdb.com/api.php?amount={amounts[amout_idx]}&category={cat['id']}&type=multiple&token={self.token}"
                res = requests.get(url)
                data = res.json()

                response_code = data.get("response_code", 2)
                if response_code == 0:
                    questions = data.get("results", [])
                    if not questions:
                        break

                    new = 0
                    for q in questions:
                        standardize_question = self.standardize_opentdb_question(q)

                        if self.question_exists(standardize_question["question"]):
                            continue

                        if self.insert_question(standardize_question):
                            new += 1

                    print(f"➕ {new} questions ajoutées.")

                elif response_code in [1, 4]:
                    amout_idx += 1
                    if amout_idx >= len(amounts):
                        break
                    else:
                        continue

                elif response_code == 5:
                    sleep(5)
                    continue
                elif response_code in [2, 3]:
                    break

    def standardize_opentdb_question(self, q):
        return {
            "question": q["question"],
            "correct_answer": q["correct_answer"],
            "incorrect_answers": q["incorrect_answers"],
            "category": q.get("category", ""),
            "difficulty": q.get("difficulty", ""),
            "type": q.get("type", ""),
            "source": "OpenTDB"
        }
    
    def get_session_token(self):
        res = requests.get("https://opentdb.com/api_token.php?command=request")
        self.token = res.json()['token'] if res.status_code == 200 else ""
        return self.token