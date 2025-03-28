from datetime import timedelta

from openai import OpenAI

from gpt_lit_reviewer.scholar_api import *
from gpt_lit_reviewer.seeker import *

def main(api_key: str):
    seed_papers = { # can be arxiv ID, DOI, or Semantic Scholar ID
        'Jukebox': 'arXiv:2005.00341', 
        'MusicGen': 'arXiv:2306.05284', 
        'MuseCoco': 'arXiv:2306.00110', 
    }

    PROMPT = '''
    I'm finetuning foundation language models of symbolic music. I'm specifically looking for papers that introduce a new foundation model for music, both audio and symbolic. The generation modality must be music, not text. Exclude literature reviews.

    Evaluate if the following paper fits the criteria.

    <paper>
    %s
    </paper>

    Does the above paper fit the criteria? Be strict and don't admit loosely-related works. Answer "Yes" or "No", using exactly one single word.
    '''.strip()

    scholarApi = ScholarAPI(timedelta(days=1))

    impactful_citers = {}
    for desc, paper_id in seed_papers.items():
        papers = scholarApi.getPapersThatCite(paper_id, fields=[
            PAPERID, TITLE, ABSTRACT, CITATIONCOUNT, YEAR, 
            EXTERNALIDS, 
        ], limit=500)
        print('# papers citing', desc, ':', len(papers))
        impactful = [*filterByImpact(papers, cites_per_year_threshold=40)]
        print(f'impactful % = {len(impactful) / len(papers):.0%}')
        impactful_citers[desc] = impactful
    
    union = verboseUnion(impactful_citers.values())
    
    if input('Proceed? y/n >').lower() != 'y':
        print('aborted')
        return

    amendAbstracts(union)

    # GPT_MODEL = "gpt-3.5-turbo"
    # GPT_MODEL = "gpt-3.5-turbo-16k"
    # GPT_MODEL = "gpt-4"
    # GPT_MODEL = "gpt-4-32k"
    # GPT_MODEL = "gpt-4-turbo-preview"
    # GPT_MODEL = "o3-mini"
    GPT_MODEL = "gpt-4o-mini"

    print('Creating OpenAI client...')
    client = OpenAI(api_key=api_key)
    print('ok')

    ratedPapers = []
    arbiter = Arbiter(client, timedelta(weeks=6))
    for paper in union:
        print()
        print(paper[TITLE])
        score = ratePaper(
            arbiter, GPT_MODEL, PROMPT, paper,
        )
        ratedPapers.append((paper, score))
        relevance = format(score, '.3%')
        print(f'{relevance = }')
    
    showAndSaveResults(ratedPapers, './results.txt', './results.csv')

if __name__ == '__main__':
    main(api_key = 'somehow supply your openai api key')
