from functools import lru_cache

import numpy as np
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

import workspace
from load_key import loadKey

# GPT_MODEL = "gpt-3.5-turbo"
# GPT_MODEL = "gpt-3.5-turbo-16k"
# GPT_MODEL = "gpt-4"
# GPT_MODEL = "gpt-4-32k"
GPT_MODEL = "gpt-4-turbo-preview"

MAX_N_TOKENS = 8

# FUNCTION = dict(
#     name='rateRelevance', 
#     parameters=dict(
#         type='object',
#         properties=dict(),
#         required=True,
#     ),
# )

@lru_cache(maxsize=1)
def client():
    print('Creating OpenAI client...')
    c = OpenAI(api_key=loadKey())
    print('ok')
    return c

def rate(paper_info: str):
    prompt = ChatCompletionUserMessageParam(
        content=workspace.PROMPT % (
            paper_info.strip()
        ), 
        role='user', 
    )
    print(prompt)
    assert False
    response = client().chat.completions.create(
        model=GPT_MODEL, 
        messages=[prompt], 
        max_tokens=MAX_N_TOKENS,
        temperature=0,    # should be inconsequential. 
        logprobs=True,
        top_logprobs=5,
    )
    choice = response.choices[0]
    lp = choice.logprobs
    assert lp is not None
    c = lp.content
    assert c is not None
    yes, no = None, None
    for top in c[0].top_logprobs:
        if top.token == 'Yes':
            yes = np.exp(top.logprob)
        elif top.token == 'No':
            no = np.exp(top.logprob)
    if yes is None or no is None:
        print(f'{c[0].top_logprobs = }')
        assert False
    return yes / (yes + no)

if __name__ == '__main__':
    loadKey()
    rate('PLACEHOLDER')
