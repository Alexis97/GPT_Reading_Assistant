import gradio as gr
import os

from utils import * 

def summarize_document(file):
    # Your summarization logic here
    # ...
    raw_text = "This is an example PDF text"
    summary = "This is an example summary"
    return raw_text, summary

# # Custom PDF Reader component
# class PDFReader(gr.inputs.Input):
#     def __init__(self):
#         super().__init__(type="file", label="Upload Document", multiple=False, accept=".pdf")

# # Custom Summary component
# class Summary(gr.outputs.Output):
#     def __init__(self):
#         super().__init__(type="html", label="Summary")


# * Create the Gradio interface
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            file_input = gr.inputs.File(label="Upload Document")
        with gr.Column():
            summary_btn = gr.Button("📝Summarize")

    
    with gr.Row():
        pdf_text_output = gr.outputs.Textbox(label="PDF Content").style(height="80%")
        summary_output = gr.outputs.Textbox(label="Summary").style(height="80%")

    # * Trigger the events
    summary_btn.click(
        fn=summarize_document,
        inputs=[file_input],
        outputs=[pdf_text_output, summary_output],
    )

# * Launch the Gradio app
PORT = find_free_port()
print(f"URL http://localhost:{PORT}")
auto_opentab_delay(PORT)
demo.queue().launch(server_name="0.0.0.0", share=False, server_port=PORT)