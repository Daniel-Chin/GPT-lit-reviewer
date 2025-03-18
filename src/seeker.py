import typing as tp
import csv
import pickle

from matplotlib import pyplot as plt
from tqdm import tqdm

from scholar_api import *
from gpt import rate

CITERS = 'citers.pickle'
RATED = 'rated.pickle'

def getAll(paper_id: str):
    papers = getPapersThatCite(paper_id)
    print('Found papers:', len(papers))
    with open(CITERS, 'wb') as f:
        pickle.dump(papers, f)

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
