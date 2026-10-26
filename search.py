import re, sqlite3, sys
from collections import defaultdict, Counter

def words(t):
    return re.findall(r"\w+", t.lower())

db = sqlite3.connect("pages.db")
pages = db.execute("SELECT url, title, body FROM pages").fetchall()

index = defaultdict(dict)
for i, (url, title, body) in enumerate(pages):
    for w, c in Counter(words(body)).items():
        index[w][i] = index[w].get(i, 0) + c
    for w in set(words(title)):
        index[w][i] = index[w].get(i, 0) + 5

def search(q, n=5):
    ws = words(q)
    if not ws:
        return []
    ok = set.intersection(*[set(index.get(w, {})) for w in ws])
    scored = sorted(((sum(index[w][i] for w in ws), i) for i in ok), reverse=True)
    return scored[:n]

def snippet(body, w):
    pos = body.lower().find(w)
    if pos < 0:
        return body[:80]
    return "..." + body[max(0, pos - 30):pos + 50] + "..."

q = " ".join(sys.argv[1:]) or input("search: ")
res = search(q)
print(len(res), "result(s) for:", q)
for score, i in res:
    url, title, body = pages[i]
    print("-", title, "|", url, "| score", score)
    print("  ", snippet(body, words(q)[0]))
