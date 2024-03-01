import openai

import workspace
from scholar_api import *

def main():
    papers = getPapersThatCite(workspace.PAPER_ID)
    for paper in papers:
        print(paper[TITLE])

if __name__ == '__main__':
    main()
