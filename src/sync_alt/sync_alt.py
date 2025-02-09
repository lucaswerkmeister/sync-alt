#!/usr/bin/env python3¿
import bs4
from collections.abc import Hashable
import os
import shutil
from typing import Callable, cast, overload
import warnings


def default_keyer(img_tag: bs4.Tag) -> str:
    src = img_tag.attrs.get("src")
    assert src is not None, f"<img> must have src= attribute: {img_tag}"
    assert isinstance(src, str)
    return src


# no bytes support, too complicated for mypy and not needed
type PathLike = os.PathLike[str] | str


@overload
def scan_directory(path: PathLike) -> dict[str, str]: ...


@overload
def scan_directory[K: Hashable](
    path: PathLike, keyer: Callable[[bs4.Tag], K]
) -> dict[K, str]: ...


def scan_directory[K: Hashable](
    path: PathLike, keyer: Callable[[bs4.Tag], K] | None = None
) -> dict[K, str]:
    """Walk the directory tree, extracting alt texts.

    Parses each HTML file found,
    and returns a dict with the alt text for each <img> that already has it.
    The key of the dict is determined by the given keyer function
    (defaults to the src= attribute of the <img>).
    """
    if keyer is None:
        # the overloads and this unconventional way of specifying the default keyer
        # are needed to work around a mypy bug; workaround courtesy of:
        # https://github.com/python/mypy/issues/10854#issuecomment-1663125865
        keyer = cast(Callable[[bs4.Tag], K], default_keyer)
    alts = {}  # type: dict[K, str]

    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith(".html"):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                soup = bs4.BeautifulSoup(f, "html.parser")
            for img in soup.find_all("img"):
                img = cast(bs4.Tag, img)  # not a NavigableString
                try:
                    alt = img.attrs["alt"]
                except KeyError:
                    continue
                alt = cast(str, alt)  # not an AttributeValueList
                key = keyer(img)
                try:
                    previous_alt = alts[key]
                except KeyError:
                    alts[key] = alt
                else:
                    if previous_alt == alt:
                        continue
                    warnings.warn(
                        f"The image {key} has conflicting alt texts:\n"
                        f"{alt} in {file_path},\n"
                        f"{previous_alt} elsewhere."
                    )
                    # keep using previous_alt
    return alts


@overload
def copy_directory(
    src: PathLike,
    dst: PathLike,
) -> None: ...


@overload
def copy_directory[K: Hashable](
    src: PathLike,
    dst: PathLike,
    keyer: Callable[[bs4.Tag], K],
) -> None: ...


def copy_directory[K: Hashable](
    src: PathLike,
    dst: PathLike,
    keyer: Callable[[bs4.Tag], K] | None = None,
) -> None:
    if keyer is None:
        keyer = cast(Callable[[bs4.Tag], K], default_keyer)
    alts = scan_directory(src, keyer)

    def copy(src: str, dst: str) -> None:
        if not src.endswith(".html"):
            return shutil.copy2(src, dst)
        modified = False
        with open(src, "r") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")
        for img in soup.find_all("img"):
            img = cast(bs4.Tag, img)  # not a NavigableString
            if "alt" in img.attrs:
                continue
            key = keyer(img)
            try:
                img.attrs["alt"] = alts[key]
            except KeyError:
                continue
            else:
                modified = True
        if not modified:
            return shutil.copy2(src, dst)
        with open(dst, "w") as f:
            f.write(str(soup))
        shutil.copystat(src, dst)

    shutil.copytree(src, dst, copy_function=copy)


def main() -> None:
    copy_directory("/tmp/LucasWerkmeistr-status", "/tmp/LucasWerkmeistr-status-synced")
