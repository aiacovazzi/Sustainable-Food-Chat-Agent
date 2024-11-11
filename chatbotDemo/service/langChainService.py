import os
import re
import dto.responseClass as rc
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv
MODEL = 'openai'
TOKEN_REGEX = r"TOKEN -?\d+(\.\d+)?"
INFO_REGEX_ANGULAR = r"<(.*?)>"
# Regex to find JSON objects (limited to one level of nesting)
INFO_REGEX_CURLY = r'\{[^{}]*\}(?:,\s*\{[^{}]*\})*'

# Load environment variables from .env file
# Other available models:
# https://openai.com/api/pricing/
# gpt-3.5-turbo-0125
# gpt-4o-mini
# gpt-4o-2024-08-06
# gpt-4

load_dotenv(find_dotenv())

if(MODEL == 'openai'):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-2024-08-06")

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
    action = get_token(answer)
    info = get_info(answer)
    answer = clean_answer_from_token_and_info(answer, info)
    response = rc.Response(answer,action,info)
    return response

def get_token(answer):
    action = re.search(TOKEN_REGEX, answer)
    action = action.group()
    return action

def get_info(answer):
    info_angular = re.search(INFO_REGEX_ANGULAR, answer)
    if info_angular != None:
        info_angular = info_angular.group()
    else:
        info_angular = ""

    info_curly = re.search(INFO_REGEX_CURLY, answer)
    if info_curly != None:
        info_curly = info_curly.group()
    else:
        info_curly = ""

    return info_angular + " " + info_curly

def clean_answer_from_token_and_info(answer, info):
    answer = re.sub(TOKEN_REGEX, "", answer)
    answer = re.sub(INFO_REGEX_ANGULAR, "", answer)
    answer = re.sub(INFO_REGEX_CURLY, "", answer)

    # Remove leading and trailing whitespace when info is not empty
    # this because in this situation the answer will be empty, so must ensure that there are no leading or trailing whitespaces
    if(info != ""):
        answer = answer.strip()
    return answer