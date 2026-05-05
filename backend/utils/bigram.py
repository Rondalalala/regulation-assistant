def _bigrams(text: str):
    chars = list(text.lower().replace(" ", "").replace("\t", "").replace("\n", ""))
    return set(chars[i] + chars[i + 1] for i in range(len(chars) - 1))


def bigram_score(query: str, text: str) -> float:
    if not query or not text:
        return 0.0
    q_grams = _bigrams(query)
    if not q_grams:
        return 0.0
    t_grams = _bigrams(text)
    hits = sum(1 for g in q_grams if g in t_grams)
    return hits / len(q_grams)
