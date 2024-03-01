from typing import *
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

PaperID = str

def unwrapResponse(response: requests.Response):
    if response.status_code == 200:
        return response.json()['data']
    raise RuntimeError(f'''HTTP status {response.status_code}: {
        response.reason
    }. \n{response.text}''')

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

def getPaperDetails(paperId: PaperID, fields: List[str]):
    RESOURCE = f'paper/{paperId}'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
        fields=','.join(fields), 
    ))
    return unwrapResponse(response)

def getPapersThatCite(cited: PaperID, fields: List[str] = [
    PAPERID, TITLE, ABSTRACT, 
]):
    RESOURCE = f'paper/{cited}/citations'
    response = requests.get(BASE_URL + RESOURCE, params=dict(
        fields=','.join(fields),
    ))
    return unwrapResponse(response)

if __name__ == '__main__':        
    from console import console
    console({**globals(), **locals()})
