import os
import openai
import json
import time

openai.api_key = os.getenv("OPENAI_API_KEY")
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)

with open('random_bash.txt', 'a') as the_file:
    start=1
    end=4000
    prompts=["Generate bash command and do not include example: \n" for _ in range(10)]
    for i in range(start, end):
        response = completion_with_backoff(
          model="text-davinci-003",
          prompt=prompts,
          temperature=1,
          max_tokens=256,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        if (i-start) % 2 ==0:
            print(i)
        for k in range(10):
            cmd=response.choices[k].text
            if cmd.startswith("\n"):
                if "\n" not in cmd[1:]:
                    the_file.write(cmd[1:]+"\n")


# with open('valid_bash2.txt') as the_file2:
#     content_list = [line for line in the_file2]

with open('/Users/Desktop/chatgpt-api/nl2bash-data.json') as user_file:
  file_contents = user_file.read()
parsed_json = json.loads(file_contents)

with open('/Users/Desktop/chatgpt-api/nl2bash-data_new_eng.json', 'a') as the_file:
    end=10348
    start=10338
    step=10
    for i in range(start, end, step):
        prompts = []
        for k in range(i, i+10):
            prompt="Translate to english:\n"+parsed_json[str(k)]["cmd"]+"\n"
            prompts.append(prompt)
        response = completion_with_backoff(
          model="text-davinci-003",
          prompt=prompts,
          temperature=0,
          max_tokens=256,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        if (i-start) % 20 ==0:
            print(i)
        for choice in response.choices:
            invocation=choice.text
            if invocation.startswith("\n"):
                invocation=invocation[1:]
            my_json_string = json.dumps({'invocation': invocation, 'cmd': prompts[choice.index][22:-1]})
            the_file.write("\"" + str(choice.index + i+1) + "\": " + my_json_string + ",\n")

