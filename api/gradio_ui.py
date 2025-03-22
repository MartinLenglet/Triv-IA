import gradio as gr
import pandas as pd

class GradioUI():
    def __init__(
        self,
        server_ip,
        port,
        db_manager,
        reranker_model,
    ):
        self.server_ip = server_ip
        self.port = port
        self.db_manager = db_manager
        self.reranker_model = reranker_model

    @property
    def all_categories(self):
        return self.db_manager.get_all_categories()
    
    def search_questions(self, search_term):
        """Fonction appelée par Gradio pour afficher le tableau filtré"""
        return gr.update(value=self.db_manager.load_questions_as_dataframe(search_term))
    
    def semantic_search(self, theme, selected_category):
        """Recherche sémantique avec scoring"""
        all_questions_df = self.db_manager.load_questions_as_dataframe()

        # Filtrer par catégorie si sélectionnée
        if selected_category:
            all_questions_df = all_questions_df[all_questions_df["category"].isin(selected_category)]

        question_texts = all_questions_df["question"].tolist()

        reranked_questions, scores = self.reranker_model.rerank_questions(theme, question_texts)
        reranked_questions_dict = [{"question": question, "score": round(score, 3)} for question, score in zip (reranked_questions, scores)]
        reranked_df = pd.DataFrame(reranked_questions_dict)

        merged_df = pd.merge(reranked_df, all_questions_df, on="question", how="left")
        columns = ["score", "question", "correct_answer", "incorrect_answers", "category", "difficulty", "source"]
        merged_df = merged_df.sort_values(by="score", ascending=False)

        # Convertir les scores en chaînes de caractères avec trois décimales pour Gradio
        merged_df['score'] = merged_df['score'].apply(lambda x: f"{x:.3f}")

        return gr.update(value=merged_df[columns])
    
    def launch_ui(self):
        with gr.Blocks() as demo:
            with gr.Tab("Toutes les questions"):
                gr.Markdown("### 📚 Base de questions de culture générale")
                with gr.Row():
                    search_box = gr.Textbox(label="Entrez un thème")
                
                with gr.Row():
                    data_output = gr.Dataframe(
                        headers=["Question", "Bonne réponse", "Mauvaises réponses", "Catégorie", "Difficulté", "Source"],
                        value=self.db_manager.load_questions_as_dataframe(),
                        interactive=False,
                        row_count=5,
                        datatype=["str"] * 6,
                        column_widths=["41%", "20%", "15%", "10%", "7%", "7%"],
                        show_search="search",
                        wrap=True,
                    )

            with gr.Tab("Recherche sémantique"):
                gr.Markdown("### 📚 Par recherche sémantique")
                with gr.Row():
                    semantic_search_box = gr.Textbox(label="Entrez un thème")
                    category_dropdown = gr.Dropdown(
                        label="Catégorie",
                        choices=self.all_categories,
                        multiselect=True
                    )
                with gr.Row():
                    search_button = gr.Button("🔍 Rechercher", scale=0)

                with gr.Row():
                    data_output_semantic_search = gr.Dataframe(
                        headers=["Score", "Question", "Bonne réponse", "Mauvaises réponses", "Catégorie", "Difficulté", "Source"],
                        interactive=False,
                        wrap=True,
                        row_count=30,
                        datatype=["str"] * 7,
                        column_widths=["5%", "41%", "20%", "10%", "10%", "7%", "7%"],
                        show_search="search",
                    )

            search_box.change(
                self.search_questions,
                inputs=search_box,
                outputs=data_output
            )

            search_button.click(
                fn=self.semantic_search,
                inputs=[semantic_search_box, category_dropdown],
                outputs=data_output_semantic_search
            )

        demo.launch(
            share=False,
            server_name=self.server_ip,
            server_port=self.port
        )