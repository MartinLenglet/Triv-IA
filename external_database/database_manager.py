import sqlite3
import pandas as pd
import html
import json

from env import DATABASE_PATH

# Classe générique de gestion de base de données
class DatabaseManager:
    def __init__(
        self, 
        db_path=DATABASE_PATH,
    ):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """Fermeture propre de la base"""
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def execute(self, query, params=None):
        """Exécution d’une requête SQL"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)

    def commit(self):
        """Validation des changements"""
        self.conn.commit()

    def create_questions_table(self):
        """Création de la table questions si elle n'existe pas"""
        self.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE,
            correct_answer TEXT,
            incorrect_answers TEXT,
            category TEXT,
            difficulty TEXT,
            type TEXT,
            source TEXT
        )
        """)
        self.commit()

    def load_questions_as_dataframe(self, search_term=""):
        """Charge les questions depuis la base sous forme de DataFrame, avec filtre facultatif"""
        self.connect()
        query = """
            SELECT question, correct_answer, incorrect_answers, category, difficulty, source
            FROM questions
        """
        df = pd.read_sql_query(query, self.conn)
        self.close()

        if search_term:
            df = df[df["question"].str.contains(search_term, case=False, na=False)]

        return df
    
    def get_all_categories(self) -> list:
        """Retourne la liste des catégories distinctes"""
        self.connect()
        query = "SELECT DISTINCT category FROM questions ORDER BY category"
        categories = [row[0] for row in self.cursor.execute(query).fetchall()]
        self.close()
        return categories
    
    def insert_question(self, standardized_question):
        """
        Insère une question au format standard :
        {
            "question": str,
            "correct_answer": str,
            "incorrect_answers": list[str],
            "category": str,
            "difficulty": str,
            "type": str,
            "source": str
        }
        """
        try:
            self.execute("""
            INSERT INTO questions (
                question, correct_answer, incorrect_answers,
                category, difficulty, type, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                html.unescape(standardized_question["question"]),
                html.unescape(standardized_question["correct_answer"]),
                json.dumps(standardized_question["incorrect_answers"]),
                standardized_question.get("category", ""),
                standardized_question.get("difficulty", ""),
                standardized_question.get("type", ""),
                standardized_question.get("source", "unknown")
            ))
            return True
        except sqlite3.IntegrityError:
            return False
        
    def question_exists(self, question_text):
        """Vérifie si une question existe déjà dans la base de données"""
        self.execute("SELECT 1 FROM questions WHERE question = ?", (question_text,))
        return self.cursor.fetchone() is not None