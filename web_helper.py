import urllib.request
import urllib.error
import ssl

G = "\033[92m"
C = "\033[96m"
Y = "\033[93m"
R = "\033[91m"
B = "\033[1m"
E = "\033[0m"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) TermuxHelper/0.3"
}

def normalize_url(raw):
    raw = raw.strip()
    if not raw or raw.startswith("curl ") or " " in raw:
        return None
    if not raw.startswith(("http://", "https://")):
        raw = "http://" + raw
    return raw

def fetch(url, method="GET", headers=None, data=None, timeout=10):
    hdrs = dict(DEFAULT_HEADERS)
    if headers:
        hdrs.update(headers)
    body = data.encode("utf-8") if isinstance(data, str) else data
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read() if e.fp else b""
    except Exception as e:
        return None, {}, str(e).encode("utf-8", errors="ignore")

def quick_status():
    url = normalize_url(input(f"{C}Target URL (in-scope): {E}"))
    if not url:
        print(f"{R}[!] Invalid URL. Enter a clean URL like http://example.com{E}")
        return
    status, hdrs, content = fetch(url)
    if status is None:
        print(f"{R}[Error] {content.decode(errors='ignore')}{E}")
        return
    sc = G if status == 200 else (Y if status in (301, 302, 403) else R)
    print(f"\n{G}[+] URL:{E} {url}")
    print(f"{G}[+] Status:{E} {sc}{status}{E} | {C}Size:{E} {len(content)}B")
    interesting = ["Server", "Content-Type", "X-Frame-Options", "X-XSS-Protection", "X-Content-Type-Options", "Content-Security-Policy", "Location", "Set-Cookie"]
    for k in interesting:
        for hk, hv in hdrs.items():
            if hk.lower() == k.lower():
                print(f"    {Y}{hk}:{E} {hv}")

def diff_requests():
    print(f"\n{C}--- Compare Two Responses (Baseline vs Modified) ---{E}")
    u1 = normalize_url(input(f"{C}URL / Param A (Baseline): {E}"))
    u2 = normalize_url(input(f"{C}URL / Param B (Modified): {E}"))
    if not u1 or not u2:
        print(f"{R}[!] Invalid URL(s). Enter clean URLs only.{E}")
        return
    s1, _, c1 = fetch(u1)
    s2, _, c2 = fetch(u2)
    if s1 is None or s2 is None:
        print(f"{R}[!] Request failed.{E}")
        return
    print(f"\n{G}[Compare]{E}")
    print(f"  {C}A:{E} {u1} -> Status={G}{s1}{E} | Size={len(c1)}B")
    print(f"  {C}B:{E} {u2} -> Status={G}{s2}{E} | Size={len(c2)}B")
    print(f"  {Y}Size Diff:{E} {len(c2) - len(c1)}B | {Y}Status Changed:{E} {s1 != s2} | {Y}Body Changed:{E} {c1 != c2}")

def custom_request():
    url = normalize_url(input(f"{C}Target URL: {E}"))
    if not url:
        print(f"{R}[!] Invalid URL.{E}")
        return
    method = (input(f"{C}Method [GET/POST/HEAD] (default GET): {E}").strip() or "GET").upper()
    raw_hdr = input(f"{C}Extra Header (e.g. X-Test: 1, or blank): {E}").strip()
    body = input(f"{C}Body (or blank): {E}").strip()
    hdrs = {}
    if ":" in raw_hdr:
        k, v = raw_hdr.split(":", 1)
        hdrs[k.strip()] = v.strip()
    status, resp_hdrs, content = fetch(url, method=method, headers=hdrs, data=body if body else None)
    if status is None:
        print(f"{R}[Error] {content.decode(errors='ignore')}{E}")
        return
    sc = G if status == 200 else (Y if status in (301, 302, 403) else R)
    print(f"\n{G}[+] Status:{E} {sc}{status}{E} | {C}Size:{E} {len(content)}B")
    for k, v in list(resp_hdrs.items())[:10]:
        print(f"    {Y}{k}:{E} {v}")
    print(f"\n{C}--- Body Preview (first 400 chars) ---{E}")
    print(content.decode("utf-8", errors="replace")[:400])

def menu():
    while True:
        print(f"\n{G}{B}+-----------------------------------------+{E}")
        print(f"{G}{B}|      TERMUX WEB / API HELPER v0.3      |{E}")
        print(f"{G}{B}+-----------------------------------------+{E}")
        print(f"  {G}1){E} Quick Status & Security Headers")
        print(f"  {G}2){E} Compare Two Requests (Diff)")
        print(f"  {G}3){E} Custom Request (Method / Header / Body)")
        print(f"  {G}4){E} Exit")
        print(f"{G}{B}+-----------------------------------------+{E}")
        choice = input(f"{Y}Choose [1-4]: {E}").strip()
        if choice == "1":
            quick_status()
        elif choice == "2":
            diff_requests()
        elif choice == "3":
            custom_request()
        elif choice == "4":
            print(f"{C}Bye!{E}")
            break
        else:
            print(f"{R}[!] Invalid option. Enter 1, 2, 3, or 4.{E}")

if __name__ == "__main__":
    menu()
