# Academic Paper Discovery Tool

A tool that helps researchers find relevant papers by:
1. Starting from a seed paper
2. Fetching its citations using Semantic Scholar API
3. Using GPT-4 to automatically evaluate each paper's relevance to your research topic

## Setup

1. Install dependencies:
````
pip install -r requirements.txt
````

2. Set up OpenAI API key:
   - Create a file `key_location.txt`
   - In this file, write the path to another file containing your OpenAI API key
   - In that key file, write: `OPENAI_API_KEY=sk-your-key-here`

3. Create `main.py`:
   - Copy `example_main.py` to `main.py`
   - Set your `PAPER_ID` (can be arxiv ID, DOI, or Semantic Scholar ID)
   - Modify the `PROMPT` to describe your research interest

## Usage

1. Run the main script:
````
python main.py
````

2. The script will:
   - Fetch papers citing your seed paper
   - Use GPT to evaluate each paper's relevance
   - Save results in `results.csv` and `results.txt`
   - Generate a histogram of relevance scores

## Output Files

- `results.csv`: CSV file containing paper titles, abstracts, and relevance scores
- `results.txt`: Human-readable format of the same results
- A histogram plot showing the distribution of relevance scores

## Dependencies

- OpenAI API (gpt-4-turbo-preview)
- Semantic Scholar API
- Python packages listed in requirements.txt

## Note

This tool requires:
- A valid OpenAI API key
- Internet connection to access Semantic Scholar API
- A relevant seed paper ID to start the search

The tool saves intermediate results, so you can interrupt and continue the process later using `continue_from_interrupted=True` in `rateThem()`. 

## Todo
- Investigate batch API.  

## Acknowledgement
Thank you to arXiv for use of its open access interoperability.
