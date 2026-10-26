# Topic 1: Google kaise bana
- Larry Page + Sergey Brin, Stanford, 1996 (pehle naam BackRub)
- Core idea PageRank: jis page ko zyada pages link karein, wo zyada important (link = vote)
- 3 hisse: crawler (pages download) -> index (words ka database) -> ranking (kaun upar)
- Sasti shuruaat: aam PCs, garage, chhota paisa; kamai ads se baad mein
- Mera plan: chhota search engine Termux mein, sirf seekhne ke liye (Python + SQLite + Flask)
- Rule: crawler sirf apni site ya allowed sites pe chalana

# Topic 2: Page download + links nikalna (crawl1.py)
- urlopen(url) se page ka HTML aata hai
- HTMLParser se <a href="..."> dhundhte hain
- urljoin se relative link (/about) poora link ban jaata hai
- set() se duplicate links hat jaate hain
- User-Agent mein bot ka naam dena achhi aadat hai
- Code: ~/search_engine/crawl1.py, test: python3 crawl1.py <url>

# Topic 3: Crawler + database (crawl2.py)
- Queue (list) mein URLs, seen (set) se repeat nahi
- Sirf same host ke links follow karo
- robots.txt padho (RobotFileParser) aur can_fetch se check karo
- Har request ke beech time.sleep(1), server pe load na pade
- script/style ka text hata ke title + body SQLite (pages.db) mein save
- Redirect ke baad final URL (r.geturl()) se duplicate hatao
- Private pages (/todo) robots.txt se block, crawler ko wahan nahi jaana
- Code: ~/search_engine/crawl2.py, run: python3 crawl2.py <url> <limit>

# Topic 4: Index + search (search.py)
- Inverted index: word -> kin pages mein aaya aur kitni baar
- Title ke word ko extra weight (+5)
- Multi-word search: sab words wale pages (set intersection)
- Score = word count ka total, zyada score upar
- Snippet = match ke aas-paas ka text
- Google ka PageRank (links ka vote) isse upar ki layer hai, baad mein
- Code: ~/search_engine/search.py, run: python3 search.py <words>

# Topic 5: Boilerplate hatana
- Navbar jaisa text har page pe hota hai, search result bigaadta hai
- Crawler mein <nav> ka text skip karo (script/style ki tarah)
- Zyada bada tareeka: TF-IDF (jo word kam pages mein ho, uski value zyada)
- Seekh: result ki quality data ki safai pe bhi depend karti hai

# Topic 6: PageRank (pagerank.py)
- Crawler ne links table mein (src -> dst) save kiye
- Har page ka rank shuru mein barabar (1/N)
- Har round mein page apna rank apne outgoing links mein barabar baant deta hai
- Damping factor 0.85: 15% random jump, taaki rank atke nahi
- Jis page ka koi outgoing link nahi (dangling), uska rank sab mein baant do
- 50 round baad rank stable ho jaata hai
- Zyada links milne wala page upar aata hai (Google ka asli idea)
- Chhoti site mein sab pages ek-doosre ko link karte hain, isliye rank lagbhag barabar
- Code: ~/search_engine/pagerank.py

# Topic 6 result
- /todo aur /expenses ka rank sabse zyada, par crawler unhe padh nahi paaya (private)
- Rank zyada hone ka matlab search mein dikhna nahi

# Topic 7: Web search page (webapp.py)
- Flask route / ?q=... se search chalta hai, results HTML mein dikhte hain
- render_template_string user ke text ko escape karta hai (XSS se bachav)
- Har request pe pages.db se index banta hai (chhote data ke liye theek)
- Code: ~/search_engine/webapp.py, run: python3 webapp.py, kholo: 127.0.0.1:5002

