from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl


class Feed(BaseModel):
    id: str
    url: HttpUrl


def load_feeds(path: Path = Path("feeds.yaml")) -> list[Feed]:
    with path.open("r") as f:
        data = yaml.safe_load(f)
    return [Feed(**entry) for entry in data.get("feeds", [])]


FEEDS = load_feeds()
