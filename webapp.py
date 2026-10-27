import re, sqlite3
from urllib.parse import urlparse
from collections import defaultdict, Counter
from flask import Flask, request, render_template_string

app = Flask(__name__)

def words(t):
    return re.findall(r"\w+", t.lower())

def pagerank(db):
    out = defaultdict(list)
    nodes = set()
    for s, d in db.execute("SELECT src, dst FROM links"):
        if s != d:
            out[s].append(d)
            nodes.update((s, d))
    N = len(nodes) or 1
    rank = {n: 1.0 / N for n in nodes}
    for _ in range(20):
        new = {n: 0.15 / N for n in nodes}
        lost = sum(rank[n] for n in nodes if not out[n])
        for n in nodes:
            for d in out[n]:
                new[d] += 0.85 * rank[n] / len(out[n])
        for n in nodes:
            new[n] += 0.85 * lost / N
        rank = new
    return rank

def stem(w):
    for suf in ("ing", "ers", "er", "ed", "es", "s"):
        if w.endswith(suf) and not w.endswith("ss") and len(w) - len(suf) >= 3:
            w = w[:-len(suf)]
            break
    if w.endswith("e") and len(w) > 3:
        w = w[:-1]
    return w

def sw(t):
    return [stem(w) for w in words(t)]

def nice(title, url):
    parts = [p for p in urlparse(url).path.split("/") if p]
    if not parts:
        return title or url
    name = parts[0].capitalize()
    if len(parts) > 1:
        name += ": " + parts[1].replace("-", " ")
    return name

def load():
    db = sqlite3.connect("pages.db")
    pages = db.execute("SELECT url, title, body FROM pages").fetchall()
    rank = pagerank(db)
    db.close()
    index = defaultdict(dict)
    for i, (url, title, body) in enumerate(pages):
        for w, c in Counter(sw(body)).items():
            index[w][i] = index[w].get(i, 0) + c
        for w in set(sw(title)):
            index[w][i] = index[w].get(i, 0) + 5
    return pages, index, rank

def search(q, index, n=10):
    ws = sw(q)
    if not ws:
        return []
    ok = set.intersection(*[set(index.get(w, {})) for w in ws])
    scored = sorted(((sum(index[w][i] for w in ws), i) for i in ok), reverse=True)
    return scored[:n]

def snippet(body, w):
    pos = body.lower().find(w)
    if pos < 0:
        return body[:100]
    return "..." + body[max(0, pos - 40):pos + 80] + "..."

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mini Search</title>
<style>
body{font-family:sans-serif;max-width:640px;margin:30px auto;padding:0 16px}
input{width:100%;padding:12px;font-size:16px;box-sizing:border-box;margin-bottom:8px}
button{padding:10px 18px;font-size:16px}
.r{margin:18px 0}.r a{font-size:1.1em}.u{color:gray;font-size:.8em;word-break:break-all}
</style></head><body>
<h1>Mini Search</h1>
<form><input name="q" value="{{ q }}" placeholder="Search..."><button>Search</button></form>
{% if q %}<p>{{ results|length }} result(s)</p>{% endif %}
{% for r in results %}
<div class="r"><a href="{{ r.url }}">{{ r.title }}</a>
<div class="u">{{ r.url }} | score {{ r.score }}</div>
<div>{{ r.snip }}</div></div>
{% endfor %}
</body></html>"""

@app.route("/")
def home():
    q = (request.args.get("q") or "").strip()[:100]
    results = []
    if q:
        pages, index, rank = load()
        tc = Counter(p[1] for p in pages)
        for score, i in sorted(((s * (1 + 10 * rank.get(pages[j][0], 0)), j) for s, j in search(q, index, 50)), reverse=True)[:10]:
            url, title, body = pages[i]
            results.append({"url": url, "title": nice(title, url) if tc[title] > 3 else (title or url),
                            "snip": snippet(body, stem(words(q)[0])), "score": round(score, 1)})
    return render_template_string(PAGE, q=q, results=results)

if __name__ == "__main__":
    app.run(port=5002)
