from src.seeker import *

SEED_PAPERS = { # can be arxiv ID, DOI, or Semantic Scholar ID
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

def main():
    getAll(
        SEED_PAPERS, 
        impact_filter_grace_period=1,
        impact_filter_cites_per_year_threshold=40,
        scholar_api_limit=1000, 
    )
    if input('Proceed? y/n >').lower() != 'y':
        print('aborted')
        return
    rateThem(PROMPT, continue_from_interrupted=False)
    showResults()

if __name__ == '__main__':
    main()
