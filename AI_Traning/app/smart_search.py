
import re
from collections import Counter
import math


def tokenize(text):
    return re.findall(r"\b[a-z0-9]+\b", str(text).lower())


def search_records(records, query):
    query_words = tokenize(query)

    if not records or not query_words:
        return []

    documents = []

    for record in records:
        text = " ".join([
            str(record.get("topic", "")),
            str(record.get("document", "")),
            str(record.get("section", "")),
            str(record.get("rule_or_value", "")),
            str(record.get("unit", ""))
        ])
        documents.append(tokenize(text))

    document_count = len(documents)
    query_counts = Counter(query_words)

    document_frequency = Counter()

    for words in documents:
        document_frequency.update(set(words))

    results = []

    for index, words in enumerate(documents):
        word_counts = Counter(words)
        score = 0

        for word, query_count in query_counts.items():
            if word in word_counts:
                idf = math.log(
                    (document_count + 1) /
                    (document_frequency[word] + 1)
                ) + 1

                score += query_count * word_counts[word] * idf

        if score > 0:
            result = records[index].copy()
            result["id"] = index + 1
            result["similarity"] = round(score, 3)
            results.append(result)

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results
