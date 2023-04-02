###
import gradio as gr
import os, json 

from bs4 import BeautifulSoup

from functools import partial

from langchain.prompts import PromptTemplate

from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import * 

from utils import * 
from prompts import * 
###

class DocumentReader(object):
    """ This class loads a document. """
    def __init__(self, db_dir='db', chunk_size=1000, chunk_overlap=0):
        self.db_dir = db_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.summary_dir = os.path.join(self.db_dir, "summaries")
        os.makedirs(self.summary_dir, exist_ok=True)
        
    def load(
            self, doc_path, collection_name='langchain',
            db_dir='db', chunk_size=1000, chunk_overlap=0
             ):
        """ This function loads a document. """
        loader = UnstructuredWordDocumentLoader(doc_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)

        embedding = OpenAIEmbeddings(model='text-embedding-ada-002')

        # create the vector store (if it doesn't exist)
        vectordb  = Chroma.from_documents(
            documents=chunks, embedding=embedding, persist_directory=db_dir, collection_name=collection_name
            )

        return chunks, vectordb
    
    def summarize(
            self, chunks, 
            map_prompt_template=MAP_PROMPT_TEMPLATE,
            combine_prompt_template=COMBINE_PROMPT_TEMPLATE,
            temperature=0.0, max_tokens=1000
            ):
        """ This function summarizes a document. """

        map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
        combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

        llm = ChatOpenAI(
            model_name='gpt-3.5-turbo',
            temperature=temperature,
            max_tokens=max_tokens,
            )
        
        chain = load_summarize_chain(
            llm=llm, chain_type="map_reduce",
            # prompt=PROMPT, 
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True, 
            return_intermediate_steps=True,
        )

        result = chain({"input_documents": chunks})
        
        total_summary = result["output_text"]

        chunk_summaries = []
        for chunk_doc, chunk_summary in zip(chunks, result["intermediate_steps"]):
            chunk_summaries.append({'chunk_content': chunk_doc.page_content, 'chunk_summary': chunk_summary})

        # save the summaries
        with open(os.path.join(self.summary_dir, "total_summary.json"), "w") as f:
            data = {
                "total_summary": total_summary,
                "chunk_summaries": chunk_summaries,
            }
            json.dump(data, f, indent=4, ensure_ascii=False)

        return total_summary, chunk_summaries
    
    def ask(
            self, query, vectordb,
            query_prompt_template=QUERY_PROMPT_TEMPLATE,
            temperature=0.0, max_tokens=1000
            ):
        """ This function asks a question and returns the answer from the document. """

        llm = ChatOpenAI(
            model_name='gpt-3.5-turbo',
            temperature=temperature,
            max_tokens=max_tokens,
            )
        
        query_prompt = PromptTemplate(
            template=query_prompt_template, input_variables=["context", "question"]
        )
        
        chain = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", 
            retriever=vectordb.as_retriever(),
            # memory=memory,
            chain_type_kwargs={"prompt": query_prompt},
            verbose=True,
            return_source_documents=True,
            )

        result = chain({"query": query})

        answer = result["result"]
        source_chunks = result["source_documents"]

        return answer, source_chunks


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

    chunks, vectordb = doc_reader.load(doc_path)

    answer, source_chunks = doc_reader.ask(
        query, vectordb,
        query_prompt_template=query_prompt_template,
        )

    # Combine the source document and answer side by side in HTML
    side_by_side_html = "<table style='width: 100%; border-collapse: collapse;'>"
    html = ""
    for chunk in source_chunks:
        html += "<p>" + chunk.page_content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
    side_by_side_html += "<tr>"
    side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{html}</td>"
    side_by_side_html += f"<td style='width: 50%; padding: 10px; border: 1px solid #ccc;'>{answer}</td>"
    side_by_side_html += "</tr>"
    side_by_side_html += "</table>"

    return side_by_side_html


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
                    ask_input = gr.inputs.Textbox(label="Ask a question")

                with gr.Column():
                    ask_btn = gr.Button("🤔Ask")
            with gr.Row(scale=2):
                ask_output = gr.HTML(
                    label="Answer", elem_classes='output', elem_id='ask_output',
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
            outputs=[ask_output],
        )



    # * Launch the Gradio app
    PORT = find_free_port()
    print(f"URL http://localhost:{PORT}")
    auto_opentab_delay(PORT)
    demo.queue().launch(server_name="0.0.0.0", share=False, server_port=PORT)


if __name__ == "__main__":
    main()