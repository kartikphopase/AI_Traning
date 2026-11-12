from dataclasses import dataclass


@dataclass
class Record:
    topic: str
    document: str
    section: str
    rule_or_value: str
    unit: str
    source_url: str
