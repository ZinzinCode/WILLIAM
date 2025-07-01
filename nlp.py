def check_contradiction(text, memory):
    # Appelle un LLM pour vérifier la cohérence avec la mémoire récente
    last_statements = [x["bot"] for x in memory.short_term][-5:]
    # LLM API call here
    return False  # ou True si contradiction