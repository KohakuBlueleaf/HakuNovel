import re


def parse_book_url(url: str) -> str:
    res = re.match(r".*book/(\d+)", url)
    if res is None:
        raise ValueError("url format is wrong.")
    return res.group(1)


def parse_page_url(url: str) -> tuple[str, str]:
    res = re.match(r".*book/(\d+)/(\d+)", url)
    if res is None:
        raise ValueError("url format is wrong.")
    return res.group(1), res.group(2)
