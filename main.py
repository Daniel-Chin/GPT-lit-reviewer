import csv

from matplotlib import pyplot as plt
from tqdm import tqdm

import workspace
from scholar_api import *
from gpt import rate

CITERS = 'citers.txt'
RESULTS = 'results.txt'

def main():
    papers = getPapersThatCite(workspace.PAPER_ID)
    print('Found papers:', len(papers))
    with open(CITERS, 'w', encoding='utf-8', newline='') as f:
        c = csv.writer(f)
        for paper in tqdm(papers):
            title = paper[TITLE] or 'None'
            abstract = paper[ABSTRACT] or 'None'
            print()
            print(title)
            score = rate(title + '\nAbstract: ' + abstract)
            relevance = format(score, '.3%')
            print(f'{relevance = }')
            c.writerow((title, abstract, score, relevance))
    citers = []
    with open(CITERS, 'r', encoding='utf-8') as f:
        c = csv.reader(f)
        for (title, abstract, score, relevance) in c:
            citers.append((title, abstract, float(score), relevance))
    citers.sort(key=lambda x: x[2], reverse=True)
    with open(RESULTS, 'w', encoding='utf-8') as f:
        for (title, abstract, score, relevance) in citers:
            print(relevance, file=f)
            print(title, file=f)
            print(abstract, file=f)
            print(file=f)
    plt.hist([x[2] for x in citers], bins=10)
    plt.show()

if __name__ == '__main__':
    main()
