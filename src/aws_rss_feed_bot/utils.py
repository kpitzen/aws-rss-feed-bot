from typing import Any, Dict


def merge_post_with_summary(
    entry: Dict[str, str], summary: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "published": entry["published"],
        "title": entry["title"],
        "link": entry["link"],
        "summary": summary,
    }
