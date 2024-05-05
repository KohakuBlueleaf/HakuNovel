import requests.packages.urllib3.util.ssl_

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL"

import os, sys
import asyncio

from wenku8.api import download
from wenku8.url_parser import parse_book_url
from utils.http import get_count
from utils.epub_editor import make_book
from config import config

from ebooklib import epub

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    bid = parse_book_url(input("Input book url: "))

    title, author, content = await download(bid)
    print(title, author)

    title = title.replace(":", "：")
    path = os.path.join(config["download_folder"], title)
    path = os.path.expanduser(path)

    if not os.path.isdir(path):
        os.makedirs(path)

    for i, (ep_title, ep_content) in enumerate(content.items()):
        print(ep_title)
        book = make_book(
            title, f"{title} {ep_title}", f"WENKU8_{title}", f"{author}", ep_content
        )

        book_path = os.path.join(path, f"{i+1:02}, {ep_title} {title}.epub")
        epub.write_epub(book_path, book)

    print(get_count())


if __name__ == "__main__":
    asyncio.run(main())
