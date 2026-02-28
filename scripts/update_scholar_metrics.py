from pathlib import Path
import re
from urllib.request import Request, urlopen


SCHOLAR_URL = "https://scholar.google.com/citations?hl=en&user=6ILuzfcAAAAJ&view_op=list_works&cstart=20&pagesize=20"
FALLBACK = "Citations = 3,736 · h-index = 34 · i10-index = 78"


def scholar_metric(html: str, label: str):
    pattern = rf">\s*{re.escape(label)}\s*<.*?<td class=\"gsc_rsb_std\">\s*([^<]+?)\s*</td>"
    match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = re.sub(r"[^0-9]", "", match.group(1))
    return int(value) if value else None


def fetch_metrics_text() -> str:
    try:
        request = Request(SCHOLAR_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")

        citations = scholar_metric(html, "Citations")
        h_index = scholar_metric(html, "h-index")
        i10_index = scholar_metric(html, "i10-index")

        if citations is None or h_index is None or i10_index is None:
            return FALLBACK

        return f"Citations = {citations:,} · h-index = {h_index} · i10-index = {i10_index}"
    except Exception:
        return FALLBACK


def main():
    root = Path(__file__).resolve().parents[1]
    out_file = root / "scholar_metrics.md"
    metrics_text = fetch_metrics_text()
    out_file.write_text(f"**Google Scholar metrics:** {metrics_text}\n", encoding="utf-8")


if __name__ == "__main__":
    main()