import requests
from bs4 import BeautifulSoup as BS


def write_to_file(t):
    with open('test.txt', 'w', encoding='utf-8') as f:
        f.write(t)

def get_html(url: str) -> str:
    """Get data from the Internet website."""
    r = requests.get(url)
    r.encoding = 'utf-8'
    return r.text
    # html = BS(r.content, 'html.parser')
    # return html

def main():
    url = "https://t.me/oldbutgoldbest/5983"
    html = get_html(url)
    write_to_file(html)
    # write_to_file(html)



if __name__ == '__main__':
    main()