import re


def parse_book_url(url: str) -> str:
    patterns = [
        [
            r'.*novel/(\d+/)*(\d+)/index.htm',
            2
        ],
        [
            r'.*/book/(\d+).htm',
            1
        ]
    ]
    for pattern, index in patterns:
        res = re.match(pattern, url)
        if res is not None:
            return res.group(index)
    raise ValueError('url format is wrong.')

def parse_page_url(url: str) -> tuple[str, str]:
    patterns = [
        [
            r'.*book/(\d+)/(\d+)',
            2
        ]
    ]
    for pattern, index in patterns:
        res = re.match(pattern, url)
        if res is not None:
            return res.group(index)
    raise ValueError('url format is wrong.')