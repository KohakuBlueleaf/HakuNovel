import asyncio
from distutils.log import error
import re
from json import loads, dumps

from bs4 import BeautifulSoup as Soup
from bs4 import NavigableString, Tag

from utils import aio_get
from .url_parser import parse_book_url, parse_page_url


APIS = [
    'https://www.23qb.net/book/{bid}/',
    'https://www.23qb.net/book/{bid}/{cid}_{page}.html'
]
WARNING_THERSHOLD = 20


async def read_page(
    bid: str, 
    cid: str, 
    page: int,
) -> list[str]:
    retry = 0
    while True:
        raw, status = await aio_get(APIS[1].format(
            bid = bid,
            cid = cid,
            page = page
        ))
        if status != 200:
            retry += 1
        else:
            break
        
        if retry > WARNING_THERSHOLD:
            print(f'{bid}-{cid} retry {retry} times.')
    
    try:
        soup = Soup(raw.decode('gbk', errors="replace"), features='html.parser')
    except UnicodeDecodeError as e:
        print(raw.decode('gbk', errors="replace"))
        print(bid, cid, page)
        raise e
    
    content: list[Tag] = soup.find(
        'div', {'id': 'TextContent'}
    ).find_all('p')[:-1]
    
    #check about "next page" hint
    if content[-1].has_attr('style'):
        content.pop()
    
    return [
        str(i)
            .replace('<p>', '<p>&nbsp;&nbsp;')
            .replace('[email&#160;protected]', '@')
        for i in content 
        if i.find('img') is None
    ]


async def read_chapter(
    title: str,
    bid: str,
    cid: str,
) -> list[str]:
    print(f'[Chapter] Start Download {title}')
    
    retry = 0
    while True:
        raw, status = await aio_get(APIS[1].format(
            bid = bid,
            cid = cid,
            page = 2
        ))
        if status != 200:
            retry += 1
        else:
            break
        
        if retry > WARNING_THERSHOLD:
            print(f'{bid}-{cid} retry {retry} times.')
    
    soup = Soup(raw.decode('gbk'), features='html.parser')
    
    try:
        ch_title = soup.find('div', {'id': 'mlfy_main_text'}).find('h1').text
        page_count = int(re.match(".*（\d+/(\d+)）", ch_title).group(1))
    except Exception as e:
        print(soup)
        print(f'Error {bid} {cid}')
        raise e
    
    all_pages = await asyncio.gather(*[
        read_page(bid, cid, p+1) for p in range(page_count)
    ])
    print(f'[Chapter] {title} downloaded.')
    
    return sum(all_pages, start = [])


async def download_book(
    title: str, chapters: dict[str, str]
) -> dict[str, list[str]]:
    print(f'[Episode] Start download {title}')
    all_chapter_content = await asyncio.gather(*[
        read_chapter(ch_title, *parse_page_url(ch_link))
        for ch_title, ch_link in chapters.items()
    ])
    print(f'[Episode] {title} downloaded.')
    return dict(zip(chapters, all_chapter_content))


async def get_toc(
    bid: str,
) -> tuple[str, str, dict[str, dict[str, str]]]:
    raw, _ = await aio_get(APIS[0].format(
        bid = bid
    ))
    soup = Soup(raw.decode('gbk'), features='html.parser')
    
    title = soup.find('div', {'class': 'd_title'}).find('h1').text
    author = soup.find('div', {'id': 'count'}).find('a').text
    toc: list[Tag] = soup.find(
        'ul', {'id': 'chapterList'}
    ).find_all('a')
    
    episodes: dict[str, dict[str, Tag]] = {}
    for ch in toc:
        episode, ch_title = ch.text.split(' ', 1)
        
        if episode not in episodes:
            episodes[episode] = {}
        
        episodes[episode][ch_title] = ch['href']
    
    return title, author, episodes


async def download(
    bid: str
) -> tuple[str, str, dict[str, dict[str, list[str]]]]:
    title, author, episodes = await get_toc(bid)
    
    all_episode_content = await asyncio.gather(*[
        download_book(title, ep)
        for title, ep in episodes.items()
    ])
    
    return title, author, dict(zip(episodes, all_episode_content))