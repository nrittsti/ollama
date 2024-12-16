import json
import pprint
import re
from io import StringIO
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.base.llms.types import MessageRole
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama

start_year = 2013
end_year = 2023
path = Path("data")
keyword = "Grundgehalt"
model = "llama3.2"
inflation = {
    2023: 5.9,
    2022: 6.9,
    2021: 3.1,
    2020: 0.5,
    2019: 1.4,
    2018: 1.8,
    2017: 1.5,
    2016: 0.5,
    2015: 0.5,
    2014: 1.0,
    2013: 1.5,
    2012: 1.9,
    2011: 2.2,
    2010: 1.0
}


def filter_context_by_keyword(context: str) -> str:
    lines = context.split('\n')
    for line in lines:
        if re.search(keyword, line):
            return line
    return None


def read_documents() -> str:
    buffer = StringIO()
    for year in range(start_year, end_year + 1):
        documents = SimpleDirectoryReader(input_files=[Path(path, "{year}.pdf".format(year=year))]).load_data()
        # print("\nFilename:", documents[0].metadata['file_name'])
        context = filter_context_by_keyword(documents[0].text)
        buffer.write("Dezember {year} {context}\n".format(year=year, context=context))
    return buffer.getvalue()


def chat(user_prompt: str, llm: Ollama) -> str:
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content="You are a smart helpful Assistant. Use german locale. Keep your answers brief an precisely."),
        ChatMessage(role=MessageRole.USER, content=user_prompt),
    ]
    return llm.chat(messages).message.content


def calc_overall_increase(data: list) -> float:
    overall = 0.0
    data[0]["Anstieg"] = 0.0
    for i in range(1, len(data)):
        data[i]["Anstieg"] = round((((data[i][keyword] - data[i - 1][keyword]) * 100) / data[i - 1][keyword]) - data[i]["Inflation"], 2)
        overall = round(overall + data[i]["Anstieg"], 2)
    return overall


def main():
    llm = Ollama(model=model, request_timeout=60.0, temperature=0.1)
    template = """                
                Use the following pieces of context to answer the question at the end.
                \n{context}\n
                Question: {question}
                Helpful Answer:"""

    context = read_documents()
    context = "{gehalt}\nInflation pro Jahr:\n{inflation}".format(gehalt=context, inflation=pprint.pformat(inflation))

    user_prompt = template.format(context=context,
                                  question="""Return the year, salary and the inflation from {start} to {end} in Json format. 
                                              Answer only in Json.""".format(start=start_year, end=end_year))
    response = chat(user_prompt, llm)
    print(response)
    data = json.loads(response.replace("```", ""))
    overall = calc_overall_increase(data)
    pprint.pp(data)
    print("\nYour overall salary has increased by {overall}%".format(overall=overall))


if __name__ == '__main__':
    main()