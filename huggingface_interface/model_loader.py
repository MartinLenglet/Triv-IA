from abc import ABC
import os
from time import time

class ModelLoader(ABC):
    """
    Abstract base class for loading a model and its tokenizer from Hugging Face.
    """

    def __init__(self, model_name: str, local_path: str, model_class, tokenizer_class, device):
        """
        Initialize the ModelLoader with the model name, local path, model class, and tokenizer class.

        :param model_name: The name of the model to load from Hugging Face.
        :param local_path: The local directory path where the model and tokenizer will be saved.
        :param model_class: The class of the model to load (e.g., BertModel, RobertaModel).
        :param tokenizer_class: The class of the tokenizer to load (e.g., BertTokenizer, RobertaTokenizer).
        """
        self.model_name = model_name
        self.local_path = local_path
        self.model_class = model_class
        self.tokenizer_class = tokenizer_class
        self.device = device
        self.model = None
        self.tokenizer = None

    def load_model_and_tokenizer(self):
        """
        Load the model and tokenizer using the download_if_not_exists method.

        :return: The loaded model and tokenizer.
        """
        self.download_if_not_exists()
        return self.model, self.tokenizer

    def download_if_not_exists(self):
        """
        Download the model and tokenizer if they do not exist locally.
        Save them to the specified local path.
        """
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)

        model_path = os.path.join(self.local_path, self.model_name)

        if not os.path.exists(model_path):
            start_time = time()
            print(f"Downloading Model '{self.model_name}'")

            # Download the model and tokenizer from Hugging Face
            self.model = self.model_class.from_pretrained(self.model_name).to(self.device)
            self.tokenizer = self.tokenizer_class.from_pretrained(self.model_name)

            # Save the model and tokenizer locally
            self.model.save_pretrained(model_path)
            self.tokenizer.save_pretrained(model_path)

            end_time = time()
            loading_time = end_time - start_time
            print(f"Model '{self.model_name}' downloaded in {loading_time:.2f} seconds.")
        else:
            start_time = time()
            print(f"Loading Model '{self.model_name}'")

            # Load the model and tokenizer from the local path
            self.model = self.model_class.from_pretrained(model_path).to(self.device)
            self.tokenizer = self.tokenizer_class.from_pretrained(model_path)

            end_time = time()
            loading_time = end_time - start_time
            print(f"Model '{self.model_name}' loaded from local path in {loading_time:.2f} seconds.")