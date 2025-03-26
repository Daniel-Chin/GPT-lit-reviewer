import typing as tp
import csv
import pickle
import datetime

from matplotlib import pyplot as plt
from tqdm import tqdm

from .scholar_api import *
from .gpt import rate
from .scrape_arxiv import scrapeAbsFromArxiv, Throttle

CITERS = 'citers.pickle'
RATED = 'rated.pickle'

def impactOf(paper: tp.Dict[str, tp.Any], grace_period: int):
    year: int | None = paper[YEAR]
    if year is None:
        return
    now = datetime.datetime.now()
    elapsed = max(0, now.year - year - grace_period)
    return paper[CITATIONCOUNT] / elapsed

def getAll(
    seed_papers: tp.Dict[str, str], 
    impact_filter_grace_period: int = 1, impact_filter_cites_per_year_threshold: int = 40, 
    scholar_api_limit: int = 500, 
):
    citers: tp.Dict[str, tp.Any] = {}
    for desc, paper_id in seed_papers.items():
        papers = getPapersThatCite(paper_id, fields=[
            PAPERID, TITLE, ABSTRACT, CITATIONCOUNT, YEAR, 
            EXTERNALIDS, 
        ], limit=scholar_api_limit)
        print('# papers citing', desc, ':', n_papers := len(papers))
        impactful = []
        for paper in papers:
            try:
                impact = impactOf(paper, impact_filter_grace_period)
            except ZeroDivisionError:
                impactful.append(paper) # potentially
            else:
                if impact is None:
                    impactful.append(paper)
                    continue
                if impact >= impact_filter_cites_per_year_threshold:
                    impactful.append(paper)
        print('% of impactful papers:', format(len(impactful) / n_papers, '.0%'))
        citers.update({x[PAPERID]: x for x in impactful})
    print('# total papers:', len(citers))
    n_in_semantic_scholar = 0
    n_rescued_by_arxiv = 0
    n_no_abs = 0
    throttle = Throttle(3.0)
    for p in tqdm(citers.values(), 'Scraping abstracts'):
        if p[ABSTRACT] is None:
            try:
                arxiv_id = p[EXTERNALIDS]['ArXiv']
            except KeyError:
                pass
            else:
                p[ABSTRACT] = scrapeAbsFromArxiv(throttle, arxiv_id)
            if p[ABSTRACT] is None:
                n_no_abs += 1
            else:
                n_rescued_by_arxiv += 1
        else:
            n_in_semantic_scholar += 1
    print('Abstract availability:')
    print(f'  {n_in_semantic_scholar = }')
    print(f'  {n_rescued_by_arxiv = }')
    print(f'  {n_no_abs = }')
    with open(CITERS, 'wb') as f:
        pickle.dump([*citers.values()], f)

def rateThem(prompt: str, continue_from_interrupted=False):
    with open(CITERS, 'rb') as f:
        citers = pickle.load(f)
    if continue_from_interrupted:
        with open(RATED, 'rb') as f:
            rated = pickle.load(f)
    else:
        rated = {}
    for paper in tqdm(citers):
        paper_id = paper[PAPERID]
        title = paper[TITLE] or 'None'
        abstract = paper[ABSTRACT] or 'None'
        if paper_id in rated:
            continue
        print()
        print(title)
        score = rate(prompt % (title + '\nAbstract: ' + abstract).strip())
        relevance = format(score, '.3%')
        print(f'{relevance = }')
        rated[paper_id] = (title, abstract, score, relevance)
        with open(RATED, 'wb') as f:
            pickle.dump(rated, f)

def showResults():
    with open(RATED, 'rb') as f:
        rated: tp.Dict[str, tp.Tuple] = pickle.load(f)
    papers = [*rated.items()]
    papers.sort(key=lambda x: x[1][2], reverse=True)
    with open('results.txt', 'w', encoding='utf-8') as ftxt:
        with open('results.csv', 'w', encoding='utf-8', newline='') as fcsv:
            c = csv.writer(fcsv)
            for paper_id, (title, abstract, score, relevance) in papers:
                print(relevance, file=ftxt)
                print(title, file=ftxt)
                print(abstract, file=ftxt)
                print(file=ftxt)

                c.writerow((relevance, title, abstract, paper_id))
    plt.hist([x[1][2] for x in papers], bins=10)
    plt.show()
