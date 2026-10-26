import re, sqlite3
from collections import defaultdict, Counter
from flask import Flask, request, render_template_string

app = Flask(__name__)

def words(t):
    return re.findall(r"\w+", t.lower())

def load():
    db = sqlite3.connect("pages.db")
    pages = db.execute("SELECT url, title, body FROM pages").fetchall()
    db.close()
    index = defaultdict(dict)
    for i, (url, title, body) in enumerate(pages):
        for w, c in Counter(words(body)).items():
            index[w][i] = index[w].get(i, 0) + c
        for w in set(words(title)):
            index[w][i] = index[w].get(i, 0) + 5
    return pages, index

def search(q, index, n=10):
    ws = words(q)
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
        pages, index = load()
        for score, i in search(q, index):
            url, title, body = pages[i]
            results.append({"url": url, "title": title or url,
                            "snip": snippet(body, words(q)[0]), "score": score})
    return render_template_string(PAGE, q=q, results=results)

if __name__ == "__main__":
    app.run(port=5002)
