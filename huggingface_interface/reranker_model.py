import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np

from .model_loader import ModelLoader

from env import PRETRAINED_HUGGINGFACE_MODELS_PATH

class RerankerModel(ModelLoader):
    """
    Concrete implementation of the ModelLoader class for loading a reranking model.
    """

    def __init__(
        self, 
        model_name="BAAI/bge-reranker-v2-m3", 
        local_path=PRETRAINED_HUGGINGFACE_MODELS_PATH,
        do_normalize_score=True,
        device=('cuda' if torch.cuda.is_available() else 'cpu'),
        batch_size=32,
    ):
        """
        Initialize the RerankerModel with the model name and local path.

        :param model_name: The name of the reranking model to load from Hugging Face.
        :param local_path: The local directory path where the model and tokenizer will be saved.
        """
        self.do_normalize_score = do_normalize_score
        self.batch_size = batch_size
        super().__init__(model_name, local_path, AutoModelForSequenceClassification, AutoTokenizer, device)

    def rerank_questions(self, theme: str, questions: list):
        """
        Rerank a list of questions based on their relevance to a theme.

        :param theme: The theme to compare the questions against.
        :param questions: List of questions to rerank.
        :return: A tuple containing the sorted list of questions and their corresponding scores.
        """
        all_scores = []

        # Process questions in batches
        for start_idx in range(0, len(questions), self.batch_size):
            batch_questions = questions[start_idx:start_idx + self.batch_size]
            pairs = [[theme, question] for question in batch_questions]

            # Tokenize the batch
            inputs = self.tokenizer(pairs, return_tensors="pt", truncation=True, padding=True).to(self.device)

            # Compute scores for the batch
            with torch.no_grad():
                batch_scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float().cpu().numpy()

            if self.do_normalize_score:
                batch_scores = self.normalize_score(batch_scores)

            all_scores.extend(batch_scores)

        # Sort questions by score in descending order
        sorted_questions_with_scores = sorted(zip(questions, all_scores), key=lambda x: x[1], reverse=True)

        # Unzip the sorted list into questions and scores
        sorted_questions, sorted_scores = zip(*sorted_questions_with_scores)

        return list(sorted_questions), list(sorted_scores)
    
    def normalize_score(self, score: float):
        return 1 / (1 + np.exp(-score)) # sigmoid
