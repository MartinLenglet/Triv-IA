import torch

from env import SERVER_IP, PORT
from api import GradioUI
from huggingface_interface import EmbeddingModel, RerankerModel
from external_database import TriviaSQLiteManager

if __name__ == "__main__":
    device = ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device available: {device}")

    # # Load the embedding model and tokenizer
    # embedding_model = EmbeddingModel()
    # embedding_model.load_model_and_tokenizer()

    # embedding_test = embedding_model.compute_embeddings(["hello world"])
    # print(embedding_test)

    # Load the reranker model and tokenizer
    reranker_model = RerankerModel()
    reranker_model.load_model_and_tokenizer()

    # reranked_questions, scores = reranker_model.rerank_questions("Harry Potter", ["Qui a écrit la série de romans Harry Potter ?", "De quelles couleurs est le drapeau du Canada ?"])
    # for question, score in zip(reranked_questions, scores):
    #     print(f"Question: {question}, Score: {score}")

    # Database Manager
    db_manager = TriviaSQLiteManager()

    ui = GradioUI(SERVER_IP, PORT, db_manager, reranker_model)
    ui.launch_ui()