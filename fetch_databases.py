from external_database import TriviaSQLiteManager

if __name__ == "__main__":
    db = TriviaSQLiteManager()
    db.connect()
    db.create_questions_table()
    db.get_session_token()
    db.fetch_all_questions()
    db.close()