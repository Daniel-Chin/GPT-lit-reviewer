import typing as tp
import csv
import datetime

from matplotlib import pyplot as plt
from tqdm import tqdm

from arxiv_api_python_client import ArxivAPI

from .scholar_api import *
from .gpt import Arbiter

def impactOf(paper: Paper, grace_period: int):
    year: int | None = paper[YEAR]
    if year is None:
        return
    now = datetime.datetime.now()
    elapsed = max(0, now.year - year - grace_period)
    return paper[CITATIONCOUNT] / elapsed

def filterByImpact(
    papers: tp.Iterable[Paper],
    cites_per_year_threshold: int,
    grace_period: int = 1,
):
    for paper in papers:
        try:
            impact = impactOf(paper, grace_period)
        except ZeroDivisionError:
            yield paper
            continue
        if impact is None:
            yield paper
            continue
        if impact >= cites_per_year_threshold:
            yield paper

def verboseUnion(x: tp.Iterable[tp.Iterable[Paper]], /):
    s = 0
    union: tp.Dict[PaperID, Paper] = {}
    for papers in x:
        for p in papers:
            s += 1
            paper_id = p[PAPERID]
            try:
                pp = union[paper_id]
            except KeyError:
                union[paper_id] = p
                continue
            pp.update(p)    # shallow
    print('All:', s, 'unique:', len(union), f'overlap: {(s - len(union)) / s:.0%}')
    return union.values()

def amendAbstracts(
    papers: tp.Iterable[Paper], show_progress: bool = True, 
    verbose: bool = True,
):
    n_no_abs = 0
    n_already_has = 0
    n_rescued_by_arxiv = 0
    with ArxivAPI() as (query, getCacheStats, _):
        for p in (
            tqdm(papers, 'amending abstracts')
            if show_progress else papers
        ):
            if p[ABSTRACT] is None:
                try:
                    arxiv_id = p[EXTERNALIDS]['ArXiv']
                except KeyError:
                    pass
                else:
                    feed = query(id_list=[arxiv_id])
                    entry, = feed.entries
                    summary = entry.summary
                    if summary is not None:
                        p[ABSTRACT] = summary.value
                if p[ABSTRACT] is None:
                    n_no_abs += 1
                else:
                    n_rescued_by_arxiv += 1
            else:
                n_already_has += 1
    if verbose:
        print(f'{getCacheStats() = }')
        print('Abstract availability:')
        print(f'  {n_already_has = }')
        print(f'  {n_rescued_by_arxiv = }')
        print(f'  {n_no_abs = }')

def ratePaper(arbiter: Arbiter, model: str, prompt_template: str, paper: Paper):
    title = paper[TITLE] or '[Title unavailable]'
    abstract = paper[ABSTRACT] or '[unavailable]'
    paper_desc = (title + '\nAbstract: ' + abstract).strip()
    return arbiter.judge(model, prompt_template % paper_desc)

def showAndSaveResults(
    ratedPapers: tp.Iterable[tp.Tuple[Paper, float]],
    outTxtPath: str, outCsvPath: str,
):
    sortedPapers = sorted(
        ratedPapers, key=lambda x: x[1], reverse=True,
    )
    with open(outTxtPath, 'w', encoding='utf-8') as ftxt:
        with open(outCsvPath, 'w', encoding='utf-8', newline='') as fcsv:
            c = csv.writer(fcsv)
            c.writerow(('Score', TITLE, ABSTRACT, PAPERID))
            for paper, score in sortedPapers:
                score_str = format(score, '.3%')
                title, abstract = paper[TITLE], paper[ABSTRACT]
                print(score_str, file=ftxt)
                print(title, file=ftxt)
                print(abstract, file=ftxt)
                print(file=ftxt)

                c.writerow((score_str, title, abstract, paper[PAPERID]))
    plt.hist([score for _, score in sortedPapers], bins=10)
    plt.show()
