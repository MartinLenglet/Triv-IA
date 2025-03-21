import sqlite3

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