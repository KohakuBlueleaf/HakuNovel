from ebooklib import epub


TEMPLATES = [
    '<html><body><h1>{ch_title}</h1>{content}</body></html>'
]


def make_book(
    title: str,
    book_id: str,
    author: str,
    contents: dict[str, list[str]]
) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(book_id)
    book.set_title(title)
    book.add_author(author)
    
    chapters = []
    for ch_title, ch_content in contents.items():
        new_ch = epub.EpubHtml(
            title = ch_title,
            file_name = f'{title}_{ch_title}.xhtml',
        )
        new_ch.set_content(
            TEMPLATES[0].format(
                ch_title = ch_title,
                content = ''.join(ch_content)
            )
        )
        chapters.append([
            ch_title, new_ch
        ])
        book.add_item(new_ch)
    
    book.toc = tuple(
        (
            epub.Section(title),
            (content, )
        ) for title, content in chapters
    )
    book.spine = [i[1] for i in chapters]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    return book