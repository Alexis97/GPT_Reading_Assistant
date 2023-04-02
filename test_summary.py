""" Test the summarization chain in LangChain. """

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

from langchain.chains.summarize import load_summarize_chain

from langchain.memory import ConversationBufferMemory
#%%
# * Load the docment 
doc_path = '/home/alex/interests/GPT_Reading_Assistant/data/从《尘缘》说起 (节选).docx'
persist_directory = os.path.join(os.path.dirname(doc_path), 'chroma')
loader = UnstructuredWordDocumentLoader(doc_path)
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

#%%
# * Initialize the chain
# Setup the LLM
llm = ChatOpenAI(
    model_name='gpt-3.5-turbo',
    temperature=0.0,
    # max_tokens=1000,
    streaming=True,  callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
    )

# Setup the prompt
summary_prompt_template="""请用中文简要总结以下内容:


"{text}"


简要总结:"""

MAP_PROMPT = PromptTemplate(template=summary_prompt_template, input_variables=["text"])

combine_prompt_template = """以下内容是对一篇文章的逐个段落总结，请整理这些段落总结，形成一篇完整的文章总结:


{text}


完整的文章总结:"
"""

COMBINE_PROMPT = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

chain = load_summarize_chain(
    llm=llm, chain_type="map_reduce",
    # prompt=PROMPT, 
    map_prompt=MAP_PROMPT,
    combine_prompt=COMBINE_PROMPT,
    verbose=True, 
    return_intermediate_steps=True,
    )

#%%
# * Run the chain
result = chain({"input_documents": docs})
#%%
print(result["intermediate_steps"])
print(result["output_text"])

# %%
