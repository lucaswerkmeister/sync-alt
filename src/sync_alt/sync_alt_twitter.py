import bs4
import sys
from typing import cast

from .sync_alt import copy_directory


def twitter_keyer(img_tag: bs4.Tag) -> tuple[str, str]:
    src = img_tag.attrs.get("src")
    assert src is not None, f"<img> must have src= attribute: {img_tag}"
    assert isinstance(src, str)

    article_tag = img_tag.find_parent("article")
    assert article_tag is not None, "<img> must have parent <article>: {img_tag}"
    article_tag = cast(bs4.Tag, article_tag)  # not a NavigableString
    permalink_tag = article_tag.find("a", class_="permalink")
    assert permalink_tag is not None, "<article> must contain <a class='permalink'>: {article_tag}"
    permalink_tag = cast(bs4.Tag, permalink_tag)  # not a NavigableString
    href = permalink_tag.attrs.get("href")
    assert href is not None, f"permalink must have href= attribute: {permalink_tag}"
    assert isinstance(href, str)

    return href, src


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 2:
        print("Usage: sync-alt SOURCE DEST", file=sys.stderr)
        sys.exit(1)
    [src, dst] = args
    copy_directory(src, dst, twitter_keyer)
