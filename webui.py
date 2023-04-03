###
import gradio as gr
import os, json 

from bs4 import BeautifulSoup

from functools import partial


from model import DocumentReader
from utils import * 
from prompts import * 
###

def summarize_document(
        doc_reader, file, 
        map_prompt_template=MAP_PROMPT_TEMPLATE,
        combine_prompt_template=COMBINE_PROMPT_TEMPLATE,
        debug=False
        ):
    """ This function summarizes a document. 
    
    """
    doc_path = file.name

    
    if debug:    
        # * [DEBUG] load the summary from a local summary file
        with open(os.path.join(doc_reader.summary_dir, "total_summary.json"), "r") as f:
            data = json.load(f)
            total_summary = data["total_summary"]
            chunk_summaries = data["chunk_summaries"]
    else:
        chunks, vectordb = doc_reader.load(doc_path)
        total_summary, chunk_summaries = doc_reader.summarize(chunks, map_prompt_template, combine_prompt_template)

    # Combine the original paragraphs and summaries side by side in HTML
    side_by_side_html = "<table style='width: 100%; border-collapse: collapse;'>"
    for element in chunk_summaries:
        chunk_content = element["chunk_content"]
        summary = element["chunk_summary"]

        # soup = BeautifulSoup(chunk_content, 'html.parser')
        # paragraphs = soup.prettify()
        html = "<p>" + chunk_content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"

        side_by_side_html += "<tr>"
        side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{html}</td>"
        side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{summary}</td>"
        side_by_side_html += "</tr>"
    side_by_side_html += "</table>"
    
    return side_by_side_html, total_summary


def ask_document(
        doc_reader, file, query,
        query_prompt_template=QUERY_PROMPT_TEMPLATE,
        debug=False
        ):
    """ This function answers a question about a document.
    
    """
    doc_path = file.name

    chunks, vectordb = doc_reader.load(doc_path, debug=debug)

    answer, source_chunks = doc_reader.ask(
        query, vectordb,
        query_prompt_template=query_prompt_template,
        )

    # Combine the source document and answer side by side in HTML
    side_by_side_html = "<table style='width: 100%; border-collapse: collapse;'>"
    html = ""
    for chunk_id, chunk in enumerate(source_chunks):
        html += "<p>" + chunk.page_content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
        html += "<hr>" if chunk_id < len(source_chunks) - 1 else ""

    side_by_side_html += "<tr>"
    side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{html}</td>"
    side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{answer}</td>"
    side_by_side_html += "</tr>"
    side_by_side_html += "</table>"

    return side_by_side_html, answer

def revise_document(
        doc_reader, file, 
        map_prompt_template=MAP_PROMPT_TEMPLATE,
        combine_prompt_template=COMBINE_PROMPT_TEMPLATE,
        debug=False
        ):
    pass

def main():
    # * Initialize the document reader
    doc_reader = DocumentReader()

    # * Create the Gradio interface
    with open("assets/style.css", "r", encoding="utf-8") as f:
        customCSS = f.read()
    with gr.Blocks(css=customCSS) as demo:
        with gr.Row():
            with gr.Column():
                file_input = gr.inputs.File(label="Upload Document")
           
        with gr.Tab(label="Summarize"):
            with gr.Row(scale=1):
                with gr.Column():
                    summary_btn = gr.Button("📝Summarize")
                with gr.Column():
                    summary_output = gr.outputs.Textbox(label="Summary").style(height="80%")
            with gr.Row(scale=5):
                chunks_summary_output = gr.HTML(
                    label="Paragraphs and Summaries", elem_classes='output', elem_id='chunks_summary_output',
                    )
        
        with gr.Tab(label="Ask"):
            with gr.Row(scale=1):
                with gr.Column():
                    ask_input = gr.inputs.Textbox(
                        label="Ask a question",
                        default="在这篇文章中，作者如何评价《尘缘》？"
                        )

                with gr.Column():
                    ask_btn = gr.Button("🤔Ask")
            with gr.Row(scale=1):
                with gr.Column():
                    ask_output = gr.outputs.Textbox(label="Answer")
            with gr.Row(scale=5):
                chunks_ask_output = gr.HTML(
                    label="Source Documents to Answer", 
                    elem_classes='output', elem_id='ask_output',
                    )

        with gr.Tab(label="Options"):
            with gr.Row(label="Summarization Options"):
                with gr.Column():
                    map_prompt_template = gr.inputs.Textbox(label="Map Prompt Template", default=MAP_PROMPT_TEMPLATE)
                with gr.Column():
                    combine_prompt_template = gr.inputs.Textbox(label="Combine Prompt Template", default=COMBINE_PROMPT_TEMPLATE).style(height="50%")
            with gr.Row(label="Question Answering Options"):
                with gr.Column():
                    query_prompt_template = gr.inputs.Textbox(label="Query Prompt Template", default=QUERY_PROMPT_TEMPLATE)
      
        # * Trigger the events
        summary_btn.click(
            fn=partial(summarize_document, doc_reader, debug=True),
            inputs=[file_input, map_prompt_template, combine_prompt_template],
            outputs=[chunks_summary_output, summary_output],
        )

        ask_btn.click(
            fn=partial(ask_document, doc_reader, debug=True),
            inputs=[file_input, ask_input, query_prompt_template],
            outputs=[chunks_ask_output, ask_output],
        )



    # * Launch the Gradio app
    PORT = find_free_port()
    print(f"URL http://localhost:{PORT}")
    auto_opentab_delay(PORT)
    demo.queue().launch(server_name="0.0.0.0", share=False, server_port=PORT)


if __name__ == "__main__":
    main()