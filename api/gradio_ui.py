import gradio as gr

class GradioUI():
    def __init__(
        self,
        server_ip,
        port,
    ):
        self.server_ip = server_ip
        self.port = port

    def greet(self, name):
        return f"Hello {name}!"
    
    def launch_ui(self):
        iface = gr.Interface(fn=self.greet, inputs="text", outputs="text")
        iface.launch(
            share=False,
            server_name=self.server_ip,
            server_port=self.port
        )