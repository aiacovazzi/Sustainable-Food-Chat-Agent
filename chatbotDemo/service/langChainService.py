import os
import re
import constants as p
import dto.responseClass as rc
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv
MODEL = 'openai'
TOKEN_REGEX = r"TOKEN -?\d+(\.\d+)?"
# Load environment variables from .env file
# Available models:
# gpt-3.5-turbo-0125
# gpt-4o-mini

load_dotenv(find_dotenv())

if(MODEL == 'openai'):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4")

def execute_chain(input_prompt, input_query, temperature):
    llm.temperature = temperature
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", input_prompt),
            ("human", "{query}"),
        ]
    )
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    answer = chain.invoke({ "query": input_query })
    action = get_token(input_prompt,answer)
    answer = clean_answer_from_token(answer)
    response = rc.Response(answer,action)
    return response

def get_token(current_prompt,answer):
    action = re.search(TOKEN_REGEX, answer)
    action = action.group()
    return action

def clean_answer_from_token(answer):
    return re.sub(TOKEN_REGEX, "", answer)