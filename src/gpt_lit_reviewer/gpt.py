from datetime import timedelta
import functools

import numpy as np
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletion
from cachier import cachier

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

class Arbiter:
    def __init__(
        self, 
        client: OpenAI, 
        cache_stale_after: timedelta = timedelta(weeks=6),
    ):
        '''
        `cache_stale_after` can be `timedelta.max` if `model` in `self.rate()` will always point to a specific checkpoint.
        '''
        self.client = client
    
        c = cachier(separate_files=True, stale_after=cache_stale_after)
        j = c(self.judge)
        self.judge = j   # type: ignore
    
    def judge(
        self, model: str, prompt: str, 
        max_tokens: int = 1,
    ):
        '''
        `max_tokens` can be larger if you want to debug by knowing what it wants to say.
        '''
        history = [ChatCompletionUserMessageParam(
            content=prompt, 
            role='user', 
        )]
        def f():
            return self.client.chat.completions.create(
                model=model, 
                messages=history, 
                max_tokens=max_tokens,
                temperature=0,    # should be inconsequential. 
                logprobs=True,
                top_logprobs=5,
            )
        response: ChatCompletion = callWithAutoRetry(f)
        assert isinstance(response, ChatCompletion) # for static type
        choice = response.choices[0]
        lp = choice.logprobs
        assert lp is not None
        c = lp.content
        assert c is not None
        yes, no = 0.0, 0.0
        for top in c[0].top_logprobs:
            prob: float = np.exp(top.logprob)
            if top.token == 'Yes':
                yes = prob
            elif top.token == 'No':
                no = prob
        if yes + no == 0:
            print(f'{c[0].top_logprobs = }')
            assert False
        return yes / (yes + no)
