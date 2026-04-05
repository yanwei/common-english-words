from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path


INITIAL_DATA_PATTERN = re.compile(
    r'<script id="js-initialData" type="text/json">(.*?)</script>',
    flags=re.S,
)
BLOCK_PATTERN = re.compile(r'(<h3><b>.*?</b></h3>|<p data-pid=".*?">.*?</p>)', flags=re.S)
ITEM_PATTERN = re.compile(
    r"^(?P<index>\d+)\.\s+"
    r"(?P<word>.+?)\s+-\s+"
    r"(?P<ipa>/.*?/)\s+-\s+"
    r"(?P<part_of_speech>[A-Za-z./ ]+)\s+"
    r"(?P<translation>.+)$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract the Zhihu answer's vocabulary list into a JSON file."
    )
    parser.add_argument("input_html", type=Path, help="Path to the dumped Zhihu HTML file")
    parser.add_argument("output_json", type=Path, help="Path to the output JSON file")
    return parser.parse_args()


def strip_tags(value: str) -> str:
    return unescape(re.sub(r"<.*?>", "", value)).strip()


def load_answer_content(html_text: str) -> str:
    match = INITIAL_DATA_PATTERN.search(html_text)
    if not match:
        raise ValueError("Could not locate the js-initialData payload in the HTML dump.")

    payload = json.loads(match.group(1))
    answer = payload["initialState"]["entities"]["answers"]["2022984490109207601"]
    return answer["content"]


def parse_categories(content: str) -> list[dict]:
    categories: list[dict] = []
    current_category: dict | None = None

    for block in BLOCK_PATTERN.findall(content):
        if block.startswith("<h3>"):
            current_category = {
                "title": strip_tags(block),
                "words": [],
            }
            categories.append(current_category)
            continue

        if current_category is None:
            continue

        text = strip_tags(block)
        if not text or text.startswith("Vocabineer网站总结了"):
            continue

        match = ITEM_PATTERN.match(text)
        if not match:
            raise ValueError(f"Could not parse vocabulary row: {text}")

        current_category["words"].append(
            {
                "index": int(match.group("index")),
                "word": match.group("word"),
                "ipa": match.group("ipa"),
                "partOfSpeech": match.group("part_of_speech").strip(),
                "translation": match.group("translation").strip(),
            }
        )

    return categories


def build_dataset(categories: list[dict]) -> dict:
    total_words = sum(len(category["words"]) for category in categories)
    return {
        "source": {
            "pageUrl": "https://www.zhihu.com/question/27584391/answer/2022984490109207601",
            "pageClaimedCategoryCount": 13,
            "actualHeadingCount": len(categories),
            "totalWords": total_words,
            "note": "The answer intro says 13 categories, but the body contains 14 headings.",
        },
        "categories": categories,
    }


def main() -> None:
    args = parse_args()
    html_text = args.input_html.read_text(encoding="utf-8")
    content = load_answer_content(html_text)
    categories = parse_categories(content)
    dataset = build_dataset(categories)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        f"Wrote {dataset['source']['totalWords']} words across "
        f"{dataset['source']['actualHeadingCount']} headings to {args.output_json}"
    )


if __name__ == "__main__":
    main()
