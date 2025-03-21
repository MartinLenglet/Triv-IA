import torch
from transformers import AutoModel, AutoTokenizer

from .model_loader import ModelLoader

from env import PRETRAINED_HUGGINGFACE_MODELS_PATH

class EmbeddingModel(ModelLoader):
    """
    Concrete implementation of the ModelLoader class for loading an embedding model.
    """

    def __init__(
        self, 
        model_name="BAAI/bge-m3", 
        local_path=PRETRAINED_HUGGINGFACE_MODELS_PATH,
        device=('cuda' if torch.cuda.is_available() else 'cpu'),
    ):
        """
        Initialize the EmbeddingModel with the model name and local path.

        :param model_name: The name of the embedding model to load from Hugging Face.
        :param local_path: The local directory path where the model and tokenizer will be saved.
        """
        super().__init__(model_name, local_path, AutoModel, AutoTokenizer, device)

    def compute_embeddings(self, texts: list):
        """
        Compute embeddings for a list of input texts.

        :param texts: List of strings to compute embeddings for.
        :return: NumPy array of embeddings.
        """
        # Tokenize the input texts
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(self.device)

        # Compute embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Perform pooling. In this case, cls pooling.
        sentence_embeddings = outputs[0][:, 0]

        # normalize embeddings
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings.cpu().numpy() # return embeddings as numpy arrays