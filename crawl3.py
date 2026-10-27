import sqlite3, sys, time
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
from html.parser import HTMLParser

START = sys.argv[1] if len(sys.argv) > 1 else "https://krishnaapp26.pythonanywhere.com/"
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 30
UA = "KrishnaLearnBot/0.1"
host = urlparse(START).netloc

def norm(u):
    u = u.replace("http://", "https://", 1)
    if u.endswith("/page/1/"):
        u = u[:-7]
    return u

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.text, self.title = [], [], ""
        self.skip = 0
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav"):
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.links.append(v)
    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav") and self.skip:
            self.skip -= 1
        if tag == "title":
            self.in_title = False
    def handle_data(self, data):
        if self.skip:
            return
        if self.in_title:
            self.title += data
        else:
            self.text.append(data)

rp = RobotFileParser(urljoin(START, "/robots.txt"))
try:
    rp.read()
except Exception:
    pass

db = sqlite3.connect("pages.db")
db.execute("CREATE TABLE IF NOT EXISTS pages (url TEXT PRIMARY KEY, title TEXT, body TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS links (src TEXT, dst TEXT, PRIMARY KEY (src, dst))")

queue, seen, done = [START], {START}, 0
fin = set()
while queue and done < LIMIT:
    url = queue.pop(0)
    if not rp.can_fetch(UA, url):
        print("robots blocked:", url)
        continue
    try:
        r = urlopen(Request(url, headers={"User-Agent": UA}), timeout=10)
        if "text/html" not in r.headers.get("Content-Type", ""):
            continue
        html = r.read().decode("utf-8", "ignore")
        final = norm(r.geturl())
    except Exception as e:
        print("fail:", url, e)
        continue
    if final in fin:
        continue
    fin.add(final)
    p = Page()
    p.feed(html)
    body = " ".join(" ".join(p.text).split())
    db.execute("INSERT OR REPLACE INTO pages VALUES (?,?,?)", (final, p.title.strip(), body))
    db.commit()
    done += 1
    print(done, final, "|", p.title.strip(), "|", len(body), "chars")
    for l in p.links:
        full = norm(urldefrag(urljoin(url, l))[0])
        if full.startswith("http") and urlparse(full).netloc == host:
            db.execute("INSERT OR IGNORE INTO links VALUES (?,?)", (final, full))
            if full not in seen:
                seen.add(full)
                queue.append(full)
    db.commit()
    time.sleep(1)

print("saved pages:", db.execute("SELECT COUNT(*) FROM pages").fetchone()[0])
