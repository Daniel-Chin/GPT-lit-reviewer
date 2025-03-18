from functools import lru_cache

import numpy as np
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletion

try:
    from gpt_auto_retry import callWithAutoRetry
except ImportError as e:
    module_name = str(e).split('No module named ', 1)[1].strip().strip('"\'')
    if module_name in (
        'gpt_auto_retry', 
    ):
        print(f'Missing module {module_name}. Please download at')
        print(f'https://github.com/Daniel-Chin/Python_Lib')
        input('Press Enter to quit...')
    raise e

import workspace
from load_key import loadKey

# GPT_MODEL = "gpt-3.5-turbo"
# GPT_MODEL = "gpt-3.5-turbo-16k"
# GPT_MODEL = "gpt-4"
# GPT_MODEL = "gpt-4-32k"
# GPT_MODEL = "gpt-4-turbo-preview"
# GPT_MODEL = "o3-mini"
GPT_MODEL = "gpt-4o-mini"

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

def rate(prompt: str):
    history = [ChatCompletionUserMessageParam(
        content=prompt, 
        role='user', 
    )]
    def f():
        return client().chat.completions.create(
            model=GPT_MODEL, 
            messages=history, 
            max_tokens=MAX_N_TOKENS,
            temperature=0,    # should be inconsequential. 
            logprobs=True,
            top_logprobs=5,
        )
    response: ChatCompletion = callWithAutoRetry(f)
    choice = response.choices[0]
    lp = choice.logprobs
    assert lp is not None
    c = lp.content
    assert c is not None
    yes, no = 0, 0
    for top in c[0].top_logprobs:
        if top.token == 'Yes':
            yes = np.exp(top.logprob)
        elif top.token == 'No':
            no = np.exp(top.logprob)
    if yes + no == 0:
        print(f'{c[0].top_logprobs = }')
        assert False
    return yes / (yes + no)

if __name__ == '__main__':
    loadKey()
    rate('PLACEHOLDER')
