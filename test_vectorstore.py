""" This script tests the vectorstore functions. Status: Complete. """
#%%
import os 
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import * 
#%%
# * Load the documents
doc_path = '/home/alex/interests/LangChain/data/从《尘缘》说起.docx'
persist_directory = os.path.join(os.path.dirname(doc_path), 'chroma')
loader = UnstructuredWordDocumentLoader(doc_path)
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

persist_directory = 'db'
embedding = OpenAIEmbeddings(model='text-embedding-ada-002')
vectordb = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=persist_directory)

#%%
# * Persist the vectorstore
vectordb.persist()
vectordb = None

#%%
# * Load the vectorstore
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
# %%
