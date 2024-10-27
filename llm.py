import os
from typing import List, Tuple

from langchain_ollama.chat_models import ChatOllama
from langchain_openai.chat_models import ChatOpenAI


from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import Tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages.tool import ToolCall
from langchain_experimental.utilities import PythonREPL
from langchain.prompts import PromptTemplate
from prompts import QNA_PROMPT, QNA_WITH_TOOL_PROMPT

from pprint import pprint


from dotenv import load_dotenv
load_dotenv()

# python tool
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)

# tools
tools = [
    TavilySearchResults(),
    repl_tool,
]

# llms
llm = ChatOpenAI(model="qwen2.5:7b-instruct-q8_0", base_url="http://localhost:11434/v1", api_key="ollama")
tool_caller_llm = llm.bind_tools(tools)

# prompts
qna_prompt = PromptTemplate.from_template(QNA_PROMPT)
qna_tool_prompt = PromptTemplate.from_template(QNA_WITH_TOOL_PROMPT)

# chains
qna_chain = qna_prompt | llm | StrOutputParser()
qna_tool_chain = qna_tool_prompt | llm | StrOutputParser()


# helper functions

def run_qna(question: str):
    """Receives a question and use the Rampo prompt to get an answer."""
    result = qna_chain.invoke({"question": question})
    return result

def run_tool_qna(question: str, tool_name: str, tool_description: str, tool_arguments: list, tool_result: str):
    result = qna_tool_chain.invoke({
        "question": question,
        "tool_name": tool_name,
        "tool_description": tool_description,
        "tool_arguments": tool_arguments,
        "tool_result": tool_result,
    })
    return result

# tools
def get_tool_call(instruction: str) -> ToolCall:
    """Based on a instruction returns a ToolCall"""
    tool_calls = tool_caller_llm.invoke(instruction).tool_calls
    try:
        return tool_calls[0]
    except IndexError:
        raise ValueError("No tool call found")


def identify_tool(tool_call) -> Tool:
    """Based on a tool call returns a Tool"""
    requested_tool: Tool = next((t for t in tools if t.name == tool_call['name']), None)
    
    if not requested_tool:
        raise ValueError(f"Tool {tool_call['name']} not found")
    
    return requested_tool


def execute_tool(tool: Tool, tool_call: ToolCall) -> dict:
    """Receives a tool and a tool call and tries to execute a tool based on the instruction description"""

    return tool.invoke(tool_call['args'])


if __name__ == "__main__":
    result = execute_tool("Qual a temperatura em Feira de Santana na Bahia?")
    bot_answer = qna_tool_chain.invoke({
        "question": "Qual a temperatura em Feira de Santana na Bahia?",
        "tool_name": result['tool_name'],
        "tool_description": result['tool_description'],
        "tool_arguments": result['tool_arguments'],
        "tool_result": result['tool_result']
    })


