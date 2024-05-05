import asyncio
from distutils.log import error
import re
from json import loads, dumps

from bs4 import BeautifulSoup as Soup
from bs4 import NavigableString, Tag

from utils import aio_get
from .url_parser import parse_book_url, parse_page_url


APIS = [
    "https://www.wenku8.net/novel/{bid_head}/{bid}/index.htm",
    "https://www.wenku8.net/novel/{bid_head}/{bid}/{cid}",
]
WARNING_THERSHOLD = 20
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
}


async def read_chapter(
    title: str,
    bid: str,
    cid: str,
) -> list[str]:
    print(f"[Chapter] Start Download {title}")

    retry = 0
    while True:
        raw, status = await aio_get(
            APIS[1].format(
                bid_head=str(bid).strip()[0],
                bid=bid,
                cid=cid,
            ),
            headers=HEADERS,
        )
        if status != 200:
            retry += 1
        else:
            break

        if retry > WARNING_THERSHOLD:
            print(f"{bid}-{cid} retry {retry} times.")

    try:
        soup = Soup(raw.decode("gbk", errors="replace"), features="html.parser")
        content = soup.find("div", {"id": "content"}).text
        content = content.replace("\r", "")
        content = content.replace("\n", "<br>\n")
        content = content.replace("\xa0\xa0", "&emsp;")
        content = content.replace(
            "最新最全的日本动漫轻小说 轻小说文库(http://www.wenku8.com) 为你一网打尽！",
            "",
        )
        content = content.replace("\n本文来自 轻小说文库(http://www.wenku8.com)", "")
    except UnicodeDecodeError as e:
        print(raw.decode("gbk", errors="replace"))
        print(bid, cid)
        raise e
    print(f"[Chapter] {title} downloaded.")

    return [content]


async def download_book(
    title: str, bid: str, chapters: dict[str, str]
) -> dict[str, list[str]]:
    print(f"[Episode] Start download {title}")
    all_chapter_content = await asyncio.gather(
        *[
            read_chapter(ch_title, bid, ch_link)
            for ch_title, ch_link in chapters.items()
        ]
    )
    print(f"[Episode] {title} downloaded.")
    return dict(zip(chapters, all_chapter_content))


async def get_toc(
    bid: str,
) -> tuple[str, str, dict[str, dict[str, str]]]:
    raw, _ = await aio_get(
        APIS[0].format(bid_head=str(bid).strip()[0], bid=bid), headers=HEADERS
    )
    soup = Soup(raw.decode("gbk"), features="html.parser")

    title = soup.find("div", {"id": "title"}).text
    author = soup.find("div", {"id": "info"}).text.split("作者：")[-1]
    toc: list[Tag] = soup.find("table", {"class": "css"}).find_all("td")

    episodes: dict[str, dict[str, Tag]] = {}
    episode = ""
    ch_title = ch_url = ""
    for item in toc:
        if item.get("class") == ["vcss"]:
            episode = item.text.strip()
        elif item.get("class") == ["ccss"]:
            ch_title = item.text.strip()
            if ch_title:
                ch_url = item.find("a").get("href")

        if episode not in episodes:
            episodes[episode] = {}
        elif ch_title and ch_url:
            episodes[episode][ch_title] = ch_url
            ch_title = ch_url = ""

    return title, author, episodes


async def download(bid: str) -> tuple[str, str, dict[str, dict[str, list[str]]]]:
    title, author, episodes = await get_toc(bid)

    all_episode_content = await asyncio.gather(
        *[download_book(title, bid, ep) for title, ep in episodes.items()]
    )

    return title, author, dict(zip(episodes, all_episode_content))


if __name__ == "__main__":
    title, author, contents = asyncio.run(download("3104"))
    print(title)
    print(author)
    print("=" * 50)
    for ep, ch in contents.items():
        print(ep)
        for ch_title, ch_content in ch.items():
            print(ch_title)
            print(ch_content)
        print("=" * 50)
