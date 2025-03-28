import typing as tp
from datetime import timedelta
from functools import wraps
from enum import Enum

import requests
from cachier import cachier

ENDPOINT = 'https://api.semanticscholar.org/graph/v1/'

# fields
PAPERID = 'paperId'
TITLE = 'title'
ABSTRACT = 'abstract'
VENUE = 'venue'
YEAR = 'year'
CITATIONCOUNT = 'citationCount'
INFLUENTIALCITATIONCOUNT = 'influentialCitationCount'
AUTHORS = 'authors'
CITINGPAPER = 'citingPaper'
CITIEDPAPER = 'citedPaper'
AUTHORID = 'authorId'
URL = 'url'
NAME = 'name'
AFFILIATIONS = 'affiliations'
EXTERNALIDS = 'externalIds'

# keywords
DATA = 'data'

PaperID = str
AuthorID = str
Paper = tp.Dict[str, tp.Any]

class NeighborType(Enum):
    CITER_OF = 'citations'
    CITED_BY = 'references'

def unwrapResponse(response: requests.Response):
    if response.status_code == 200:
        return response.json()['data']
    raise RuntimeError(f'''HTTP status {response.status_code}: {
        response.reason
    }. \n{response.text}''')

class ScholarAPI:
    def __init__(self, cache_max_age: timedelta):
        def enableCache(x: tp.Callable, /):
            f = cachier(separate_files=True)(x)
            c = f.caller_with_freshness_threshold   # type: ignore
            return wraps(x)(c(cache_max_age))
        for name in (
            'searchPaper', 'getPaperDetails', 'getPapersThatCite',
            'searchAuthor', 'getPapersFromAuthor',
        ):
            setattr(self, name, enableCache(getattr(self, name)))
    
    def searchPaper(self, query: str, limit: int = 3):
        RESOURCE = 'paper/search'
        response = requests.get(ENDPOINT + RESOURCE, params=dict(
            query=query, 
            limit=limit, 
        ))
        return unwrapResponse(response)

    def prettySearchPaper(self, query: str, limit: int = 3):
        papers = self.searchPaper(query, limit)
        for paper in papers:
            print(paper[PAPERID])
            print(paper[TITLE])

    def getPaperDetails(self, paperId: PaperID, fields: tp.List[str]):
        RESOURCE = f'paper/{paperId}'
        response = requests.get(ENDPOINT + RESOURCE, params=dict(
            fields=','.join(fields), 
        ))
        return unwrapResponse(response)

    def getPaperNeighbors(
        self, 
        neighborType: NeighborType, 
        paper_id: PaperID, 
        fields: tp.List[str] = [PAPERID, TITLE, ABSTRACT], 
        limit: int = 500, 
    ) -> tp.List:
        RESOURCE = f'paper/{paper_id}/{neighborType.value}'
        response = requests.get(ENDPOINT + RESOURCE, params=dict(
            fields=','.join(fields),
            limit=limit,
        ))
        papers = unwrapResponse(response)
        if len(papers) == limit:
            input('Warning: limit reached. Not all papers are fetched. Press Enter to continue.')
        return [x[{
            NeighborType.CITER_OF: CITINGPAPER,
            NeighborType.CITED_BY: CITIEDPAPER,
        }[neighborType]] for x in papers]

    def searchAuthor(self, query: str, limit: int = 3):
        RESOURCE = 'author/search'
        response = requests.get(ENDPOINT + RESOURCE, params=dict(
            query=query, 
            limit=limit, 
            fields=','.join([AUTHORID, NAME, AFFILIATIONS, URL]),
        ))
        return unwrapResponse(response)

    def getPapersFromAuthor(self, author: AuthorID, fields: tp.List[str] = [
        PAPERID, TITLE, ABSTRACT, 
    ], limit: int = 500) -> tp.List:
        RESOURCE = f'author/{author}/papers'
        response = requests.get(ENDPOINT + RESOURCE, params=dict(
            fields=','.join(fields),
            limit=limit,
        ))
        papers = unwrapResponse(response)
        if len(papers) == limit:
            input('Warning: limit reached. Not all papers are fetched. Press Enter to continue.')
        return papers

if __name__ == '__main__':        
    from console import console
    console({**globals(), **locals()})
