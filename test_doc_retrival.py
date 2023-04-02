""" This script tests the document retrieval functions. Status: Complete. """

#%%
import os 
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import * 

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from langchain.chat_models import ChatOpenAI

from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
#%%
# * Load the vectorstore
persist_directory = '/home/alex/interests/GPT_Reading_Assistant/db'
embedding = OpenAIEmbeddings(model='text-embedding-ada-002')

vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)

#%%
# * Initialize the chain
# Setup the LLM
llm = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    temperature=0.9,
    max_tokens=1000,
    streaming=True,  callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    )

# Setup the prompt
prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Always make sure you use the same language as the user asked the question in.

{context}

Question: {question}
Answer:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

doc_retrieval = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", 
    retriever=vectordb.as_retriever(),
    # memory=memory,
    chain_type_kwargs={"prompt": PROMPT},
    verbose=True,
    return_source_documents=True,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    )
#%%
query = "在这篇文章中，作者如何评价《尘缘》？"
result = doc_retrieval({"query": query})

print(result["result"])
print(result["source_documents"])
# %%
query = "作者对于《大鱼海棠》的评价是什么？"
result = doc_retrieval({"query": query})

print(result["result"])
print(result["source_documents"])
# %%
