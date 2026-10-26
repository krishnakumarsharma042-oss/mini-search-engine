import sys
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.links.append(v)

url = sys.argv[1] if len(sys.argv) > 1 else "https://krishnaapp26.pythonanywhere.com/"
req = Request(url, headers={"User-Agent": "KrishnaLearnBot/0.1"})
html = urlopen(req, timeout=10).read().decode("utf-8", "ignore")
p = LinkParser()
p.feed(html)
print("page size:", len(html))
for l in sorted(set(urljoin(url, x) for x in p.links)):
    print(l)
