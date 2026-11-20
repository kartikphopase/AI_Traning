
from data.sample_records import records


def load_records():
    return records



def search(keyword):
    results = []

    for record in records:
        if (keyword.lower() in record["topic"].lower() or
            keyword.lower() in record["rule_or_value"].lower()):
            results.append(record)

    return results



def count_by(category):
    counts = {}

    for record in records:
        value = record.get(category, "Unknown")
        counts[value] = counts.get(value, 0) + 1

    return counts



def get_by_id(record_id):
    if 1 <= record_id <= len(records):
        return records[record_id - 1]

    return None
