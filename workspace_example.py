PAPER_ID = ( # can be arxiv ID, DOI, or Semantic Scholar ID
    'af997821231898a5f8d0fd78dad4eec526acabe5'
)

PROMPT = '''
I'm writing a paper about a prompt manager that integrates an LLM into a complex system. The LLM directs the user interaction with the system. The LLM serves as the interface between the user and the system. I'm looking for related works, e.g., LLM as a controller, as a user interfaces, as a tools director, or as an assistant.

Evaluate the relevance of the following paper to my research.

<paper>
%s
</paper>

Is the above paper relevant? Answer "Yes" or "No", using exactly one single word.
'''.strip()
