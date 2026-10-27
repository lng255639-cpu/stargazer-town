"""星標鎮日報 local server.

Serves this folder and adds /api/trending, which scrapes github.com/trending
server-side (browsers can't read that page directly because of CORS).
Run:  python server.py                     then open http://localhost:8765/
      python server.py --dump trending.json   write the list once and exit (used by GitHub Actions)
"""
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8765
CACHE_SECONDS = 10 * 60
_cache = {"at": 0.0, "body": None}


def _text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment or "")).strip()


def _num(s):
    digits = re.sub(r"[^\d]", "", s or "")
    return int(digits) if digits else 0


def fetch_trending():
    req = urllib.request.Request(
        "https://github.com/trending",
        headers={"User-Agent": "Mozilla/5.0 (StargazerTown local server)", "Accept-Language": "en"},
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        page = res.read().decode("utf-8", "replace")
    repos = []
    for art in re.findall(r'<article class="Box-row">(.*?)</article>', page, re.S)[:10]:
        m = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^"]+)"', art, re.S)
        if not m:
            continue
        full = m.group(1).strip()
        desc = re.search(r"<p[^>]*>(.*?)</p>", art, re.S)
        lang = re.search(r'itemprop="programmingLanguage">([^<]*)<', art)
        stars = re.search(r'href="/[^"]+/stargazers"[^>]*>(.*?)</a>', art, re.S)
        forks = re.search(r'href="/[^"]+/forks"[^>]*>(.*?)</a>', art, re.S)
        today = re.search(r"([\d,]+)\s+stars?\s+(?:today|this week|this month)", art)
        repos.append({
            "full": full,
            "desc": _text(desc.group(1)) if desc else "",
            "lang": lang.group(1).strip() if lang else "",
            "stars": _num(_text(stars.group(1))) if stars else 0,
            "forks": _num(_text(forks.group(1))) if forks else 0,
            "today": _num(today.group(1)) if today else 0,
        })
    if not repos:
        raise RuntimeError("trending page had no repos (layout changed?)")
    return {"source": "trending", "updatedAt": datetime.now(timezone.utc).isoformat(), "repos": repos}


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] != "/api/trending":
            return super().do_GET()
        try:
            if not _cache["body"] or time.time() - _cache["at"] > CACHE_SECONDS:
                _cache["body"] = json.dumps(fetch_trending(), ensure_ascii=False).encode("utf-8")
                _cache["at"] = time.time()
            body, status = _cache["body"], 200
        except Exception as e:  # serve the last good copy if we have one
            if _cache["body"]:
                body, status = _cache["body"], 200
            else:
                body, status = json.dumps({"error": str(e)}).encode("utf-8"), 502
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def guess_type(self, path):
        t = super().guess_type(path)
        return t + "; charset=utf-8" if t in ("text/html", "text/plain", "application/javascript", "text/css") else t


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--dump":
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            json.dump(fetch_trending(), f, ensure_ascii=False, indent=1)
            f.write("\n")
        sys.exit(0)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"星標鎮日報：http://localhost:{PORT}/  (Ctrl+C 結束)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
