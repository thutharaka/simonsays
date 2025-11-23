import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    print("Please provide GEMINI_API_KEY env variable")
    exit(1)


def gemini_query(prompt: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text


def build_gemini_prompt(user_tasks: list[str], distractions: list[str]) -> str:
    prompt = "The user is doing the following tasks:"
    prompt += "\n- use a program named 'Simon Says' that monitors your health goals and current tasks"
    for task in user_tasks:
        prompt += f"\n- {task}"
    prompt += "\nThe following are snippets of text from the user's screen. For each snippet, if it is related to either one of the user's tasks, output 'KEEP'. If the snippet is unrelated and the user is distracted from their tasks, output 'KILL'. If you are unsure of what the snippet means, output 'KEEP'. You are to output only a list of KEEP's and KILL's separated by newlines corresponding to each snippet in order and nothing else. The following are the snippets:"
    for potential_distraction in distractions:
        prompt += "\n```"
        prompt += f"\n{potential_distraction}"
        prompt += "\n```"
    print(prompt)
    return prompt


def parse_gemini_results(res: str) -> list[bool]:
    kill_list = []
    for line in res.split('\n'):
        if line == "KEEP":
            kill_list.append(False)
        elif line == "KILL":
            kill_list.append(True)
        else:
            raise Exception("Gemini is being a bad.")
    return kill_list

# p = build_gemini_prompt([
#     "program a personal website",
#     "listen to music",
#     "research for upcoming project about shoes",
#     "practice programming in general"
# ], [
#     """
# Buzzworthy deals
# Black Friday
# 40 % off
# Black Friday
# Deal
# Frome
# Skylight""", """
# horizontally .
# html
# head
# style
# .center
# margin : auto
# width : 200px
# background color : lightblue
# style
# head
# body
# div class
# center
# Horizontally Centered
# div
# body
# html
# to : contere the div borizontally by distributing equal marain on both sides .""",
#                         "How to reverse a linked list"
# ])
# 
# print("###")
# 
# print(gemini_query(p))
