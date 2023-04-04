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
        doc_reader, file, templates, summary_option,
        debug=False
        ):
    """ This function summarizes a document. 
    
    """
    # Convert the templates from Gradio to a dictionary
    templates_dict = {k: v.value for k, v in templates.items()}

    doc_path = file.name
    
    chunks, vectordb = doc_reader.load(doc_path, debug=debug)
    total_summary, chunk_summaries = doc_reader.summarize(chunks, templates_dict, summary_option=summary_option, debug=debug)

    # Combine the original paragraphs and summaries side by side in HTML
    side_by_side_html = generate_side_by_side_html(chunk_summaries)
    
    return side_by_side_html, total_summary


def ask_document(
        doc_reader, file, query, templates,
        debug=False
        ):
    """ This function answers a question about a document.
    
    """
    # Convert the templates from Gradio to a dictionary
    templates_dict = {k: v.value for k, v in templates.items()}

    doc_path = file.name

    chunks, vectordb = doc_reader.load(doc_path, debug=debug)

    answer, source_chunks = doc_reader.ask(
        query, vectordb,
        query_prompt_template=templates_dict['query_prompt_template'],
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

        # templates = gr.State({})
        
        with gr.Tab(label="Options"):
            with gr.Row(label="Summarization Options"):
                with gr.Row():
                    summary_option = gr.inputs.Radio(
                        label="Summary Option",
                        choices =['map_reduced', 'refine'],
                        # label=["分段摘要", "逐步总结"],
                        default="map_reduced",
                        )
                with gr.Row():
                    with gr.Tab(label="Map-Reduce Options") as map_reduce_tab:
                        with gr.Column():
                            map_prompt_template = gr.inputs.Textbox(label="Map Prompt Template", default=MAP_PROMPT_TEMPLATE, lines=5)
                        with gr.Column():
                            combine_prompt_template = gr.inputs.Textbox(label="Combine Prompt Template", default=COMBINE_PROMPT_TEMPLATE, lines=5)
                    with gr.Tab(label="Refine Options") as refine_tab:
                        with gr.Column():
                            refine_initial_prompt_template = gr.inputs.Textbox(label="Initial Prompt Template", default=PROPOSAL_REFINE_INITIAL_TEMPLATE, lines=5)
                        with gr.Column():
                            refine_prompt_template = gr.inputs.Textbox(label="Refine Prompt Template", default=PROPOSAL_REFINE_TEMPLATE, lines=5)

            with gr.Row(label="Question Answering Options"):
                with gr.Column():
                    query_prompt_template = gr.inputs.Textbox(label="Query Prompt Template", default=QUERY_PROMPT_TEMPLATE, lines=5)

        templates = gr.State({
            'map_prompt_template': map_prompt_template,
            'combine_prompt_template': combine_prompt_template,
            'refine_initial_prompt_template': refine_initial_prompt_template,
            'refine_prompt_template': refine_prompt_template,
            'query_prompt_template': query_prompt_template,
            })
        
        
        # * Trigger the events
        def update_tabs(summary_option, map_reduce_tab, refine_tab):
            if summary_option == 'map_reduced':
                return gr.update(map_reduce_tab, visible=True), gr.update(refine_tab, visible=False)
            else:
                return gr.update(map_reduce_tab, visible=False), gr.update(refine_tab, visible=True)
            
        summary_option.change(
            fn=update_tabs,
            inputs=[summary_option, map_reduce_tab, refine_tab],
            outputs=[map_reduce_tab, refine_tab])

        summary_btn.click(
            fn=partial(summarize_document, doc_reader, debug=True),
            inputs=[file_input, templates, summary_option],
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