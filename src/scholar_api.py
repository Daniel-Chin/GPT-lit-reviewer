import typing as tp
import requests

BASE_URL = 'https://api.semanticscholar.org/graph/v1/'

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
AUTHORID = 'authorId'
URL = 'url'
NAME = 'name'
AFFILIATIONS = 'affiliations'
EXTERNALIDS = 'externalIds'

# keywords
DATA = 'data'

PaperID = str
AuthorID = str

def httpStatus(response: requests.Response):
    if response.status_code == 200:
        return response.json()
    raise RuntimeError(f'''HTTP status {response.status_code}: {
        response.reason
    }. \n{response.text}''')

def unwrapResponse(response: requests.Response):
    return httpStatus(response)['data']

def searchPaper(query: str, limit: int = 3):
    RESOURCE = 'paper/search'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
        query=query, 
        limit=limit, 
    ))
    return unwrapResponse(response)

def prettySearchPaper(query: str, limit: int = 3):
    papers = searchPaper(query, limit)
    for paper in papers:
        print(paper[PAPERID])
        print(paper[TITLE])

def getPaperDetails(paperId: PaperID, fields: tp.List[str]):
    RESOURCE = f'paper/{paperId}'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
        fields=','.join(fields), 
    ))
    return unwrapResponse(response)

def getPapersThatCite(cited: PaperID, fields: tp.List[str] = [
    PAPERID, TITLE, ABSTRACT, 
], limit: int = 500) -> tp.List:
    RESOURCE = f'paper/{cited}/citations'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
        fields=','.join(fields),
        limit=limit,
    ))
    papers = unwrapResponse(response)
    if len(papers) == limit:
        input('Warning: limit reached. Not all papers are fetched. Press Enter to continue.')
    return [x[CITINGPAPER] for x in papers]

def searchAuthor(query: str, limit: int = 3):
    RESOURCE = 'author/search'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
        query=query, 
        limit=limit, 
        fields=','.join([AUTHORID, NAME, AFFILIATIONS, URL]),
    ))
    return unwrapResponse(response)

def getPapersFromAuthor(author: AuthorID, fields: tp.List[str] = [
    PAPERID, TITLE, ABSTRACT, 
], limit: int = 500) -> tp.List:
    RESOURCE = f'author/{author}/papers'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
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
