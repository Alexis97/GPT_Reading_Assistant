import os, json 

from langchain.prompts import PromptTemplate

from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import * 

from prompts import * 

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
            db_dir='db', chunk_size=1000, chunk_overlap=0,
            debug=False
            ):
        """ This function loads a document. """
        loader = UnstructuredWordDocumentLoader(doc_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(documents)

        embedding = OpenAIEmbeddings(model='text-embedding-ada-002')

        # create the vector store (if it doesn't exist)
        if debug:
            vectordb = Chroma(persist_directory=db_dir, embedding_function=embedding, collection_name=collection_name)
        else:
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



