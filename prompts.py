MAP_PROMPT_TEMPLATE="""请用中文简要总结以下内容:


"{text}"


简要总结:"""



COMBINE_PROMPT_TEMPLATE = """以下内容是对一篇文章的逐个部分的总结，请整理这些段落总结，形成一篇完整的文章总结，注意在总结中不要出现第一部分、第二部分等描述，要让读者感觉这是一篇完整的文章:


{text}


完整的文章总结:"
"""

QUERY_PROMPT_TEMPLATE = """阅读以下内容来回答问题。 如果你不知道答案，就说你不知道，不要试图编造答案。如果你知道答案，请尽量详细具体地回答问题。

{context}

问题: {question}
答案:
"""

proposal_summary_format = """
# Project title
## Goals 
## Problem statement
## State-of-the-art
## Dataset
    - size, 
    - modality, 
    - labels, 
    - sample data visualization, 
    - justify the dataset is statistically significant
## Methods 
## Steps, timetable, and alternatives 
## Expected outcome and validation method 
## Citations (optional)
"""

PROPOSAL_REFINE_INITIAL_TEMPLATE = """You are acting as a restrict proposal reviewer. Please read the following proposal and provide a concise summary of the proposal into the following contents (report N/A if the proposal doesn't mention), with a clear Markdown format with the following template:

# Project title
## Goals 
## Problem statement
## State-of-the-art
## Dataset
    - size, 
    - modality, 
    - labels, 
    - sample data visualization, 
    - justify the dataset is statistically significant
## Methods 
## Steps, timetable, and alternatives 
## Expected outcome and validation method 
## Citations (optional)

Here is the proposal:
"{text}"

CONCISE SUMMARY:"""



PROPOSAL_REFINE_TEMPLATE = """You are acting as a restrict proposal reviewer. Your job is to produce a final summary of the proposal into the following contents (report N/A if the proposal doesn't mention), with a clear Markdown format with the following template:

# Project title
## Goals 
## Problem statement
## State-of-the-art
## Dataset
    - size, 
    - modality, 
    - labels, 
    - sample data visualization, 
    - justify the dataset is statistically significant
## Methods 
## Steps, timetable, and alternatives 
## Expected outcome and validation method 
## Citations (optional)

We have provided an existing summary up to a certain point: {existing_answer}. 
We have the opportunity to refine the existing summary (only if needed) with some more context below.

--------------
{text}
--------------

Given the new context, refine the original summary. If the context is not useful, you must copy the original summary (very important!).
"""

TRANSLATE_PROMPT_TEMPLATE = """请用中文通顺准确地翻译以下内容:

"{text}"

翻译:"""