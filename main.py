import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pathlib import Path

ISSUE_URL = "https://github.com/wzdnzd/aggregator/issues/91"
OUTPUT_FILE = Path("subscribe.txt")

headers = {
    "User-Agent": "Mozilla/5.0 (GitHub Action)"
}

resp = requests.get(ISSUE_URL, headers=headers, timeout=10)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# =========================
# 1. 抓取订阅接口 URL
# =========================
subscribe_url = None

for strong in soup.find_all("strong"):
    if strong.get_text(strip=True) == "在线服务接口地址":
        p = strong.find_parent("p")
        if p:
            a = p.find("a", href=True)
            if a:
                subscribe_url = a["href"]
        break

if not subscribe_url:
    raise RuntimeError("未找到订阅接口 URL")

# =========================
# 2. 抓取 token
# =========================
token_value = None

for tr in soup.find_all("tr"):
    tds = tr.find_all("td")
    if tds and tds[0].get_text(strip=True) == "token":
        code = tds[5].find("details")
        if code:
            token_value = code.get_text(strip=True)
        break

if not token_value:
    raise RuntimeError("未找到 token")

# =========================
# 3. 替换 token
# =========================
parsed = urlparse(subscribe_url)
query = parse_qs(parsed.query)
query["token"] = [token_value]
query["target"] = 'clash'
query["list"] = 0
final_query = urlencode(query, doseq=True)

final_url = urlunparse((
    parsed.scheme,
    parsed.netloc,
    parsed.path,
    parsed.params,
    final_query,
    parsed.fragment
))

# =========================
# 4. 写入文件
# =========================
OUTPUT_FILE.write_text(final_url + "\n", encoding="utf-8")

print("Updated subscribe URL:")
print(final_url)
