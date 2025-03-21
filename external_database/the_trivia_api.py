import requests
from time import sleep

from .database_manager import DatabaseManager

class TheTriviaAPISQLiteManager(DatabaseManager):
    def get_categories(self):
        return ["music", "sport_and_leisure", "film_and_tv", "arts_and_literature", "history", "society_and_culture", "science", "geography", "food_and_drink", "general_knowledge"]
    
    def fetch_all_questions(self, nbr_requests=5):
        categories = self.get_categories()
        for cat in categories:
            print(f"📚 Catégorie : {cat}")
            amounts = [50, 20, 10, 5, 1]
            amout_idx = 0

            for _ in range(nbr_requests):
                url = f"https://the-trivia-api.com/api/questions?limit={amounts[amout_idx]}&categories={cat}"
                res = requests.get(url)

                if res.status_code == 429: # rate limit
                    sleep(5)
                    continue
                elif res.status_code == 200:
                    data = res.json()

                    new = 0
                    for question in data:
                        standardize_question = self.standardize_opentdb_question(question)

                        if self.question_exists(standardize_question["question"]):
                            continue

                        if self.insert_question(standardize_question):
                            new += 1

                    print(f"➕ {new} questions ajoutées.")
                else:
                    print(res)

    def standardize_opentdb_question(self, q):
        return {
            "question": q["question"],
            "correct_answer": q["correctAnswer"],
            "incorrect_answers": q["incorrectAnswers"],
            "category": q.get("category", ""),
            "difficulty": q.get("difficulty", ""),
            "type": q.get("type", ""),
            "source": "TheTriviaAPI"
        }