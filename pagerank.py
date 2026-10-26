import sqlite3
db = sqlite3.connect("pages.db")
edges = [(s, d) for s, d in db.execute("SELECT src, dst FROM links") if s != d]
nodes = sorted({x for e in edges for x in e})
out = {n: [] for n in nodes}
for s, d in edges:
    out[s].append(d)
N = len(nodes)
rank = {n: 1.0 / N for n in nodes}
D = 0.85
for _ in range(50):
    new = {n: (1 - D) / N for n in nodes}
    dangling = sum(rank[n] for n in nodes if not out[n])
    for n in nodes:
        if out[n]:
            share = D * rank[n] / len(out[n])
            for d in out[n]:
                new[d] += share
    for n in nodes:
        new[n] += D * dangling / N
    rank = new
print("pages:", N, "| total rank:", round(sum(rank.values()), 4))
for n in sorted(nodes, key=rank.get, reverse=True):
    print(round(rank[n], 4), "|", len(out[n]), "out |", n)
