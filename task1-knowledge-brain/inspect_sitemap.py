"""Inspect one approved sitemap without downloading any individual article pages.

Run this only after confirming that the site's terms and crawl guidance allow
this use. A sitemap URL is a discovery source, not proof that an entry is a
support article or permission to reuse its content.
"""

from __future__ import annotations

import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


SITEMAP_URL = "https://support.brilliantdirectories.com/support/sitemap.xml"
ALLOWED_HOSTNAME = "support.brilliantdirectories.com"
OUTPUT_PATH = Path(__file__).parent / "data" / "sitemap_candidates.json"
TIMEOUT_SECONDS = 15
MAX_SITEMAP_BYTES = 5_000_000
USER_AGENT = "AI-Tech-Consultant-Capstone/0.1 (sitemap inspection)"


class SitemapFetchError(Exception):
    """Raised when the initial sitemap cannot be downloaded safely."""


class SitemapFormatError(Exception):
    """Raised when downloaded content is not a supported sitemap format."""


def local_name(element: ET.Element) -> str:
    """Return an XML tag name without its optional namespace."""

    return element.tag.rsplit("}", 1)[-1]


def child_text(parent: ET.Element, name: str) -> str | None:
    """Get the text of a direct child element, such as <loc> or <lastmod>."""

    for child in parent:
        if local_name(child) == name:
            text = (child.text or "").strip()
            return text or None
    return None


def is_allowed_support_url(url: str) -> bool:
    """Accept only HTTPS URLs whose hostname exactly matches the approved host."""

    try:
        parsed = urlsplit(url)
    except ValueError:
        return False

    return (
        parsed.scheme.lower() == "https"
        and parsed.hostname is not None
        and parsed.hostname.lower() == ALLOWED_HOSTNAME
    )


def fetch_sitemap() -> bytes:
    """Download only the configured sitemap and return its XML bytes."""

    request = Request(
        SITEMAP_URL,
        headers={
            "Accept": "application/xml, text/xml;q=0.9, */*;q=0.1",
            "User-Agent": USER_AGENT,
        },
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status_code = response.getcode()
            if status_code != 200:
                raise SitemapFetchError(
                    f"Expected HTTP 200 from the sitemap, but received {status_code}."
                )

            # Limiting the response avoids accidentally loading an unexpectedly large file.
            sitemap_bytes = response.read(MAX_SITEMAP_BYTES + 1)
    except HTTPError as error:
        raise SitemapFetchError(
            f"HTTP error {error.code} while fetching {SITEMAP_URL}: {error.reason}"
        ) from error
    except (TimeoutError, socket.timeout):
        raise SitemapFetchError(
            f"Timed out after {TIMEOUT_SECONDS} seconds while fetching {SITEMAP_URL}."
        ) from None
    except URLError as error:
        raise SitemapFetchError(
            f"Network error while fetching {SITEMAP_URL}: {error.reason}"
        ) from error
    except OSError as error:
        raise SitemapFetchError(
            f"Could not fetch {SITEMAP_URL}: {error}"
        ) from error

    if len(sitemap_bytes) > MAX_SITEMAP_BYTES:
        raise SitemapFetchError(
            f"The sitemap is larger than the {MAX_SITEMAP_BYTES:,}-byte safety limit."
        )

    return sitemap_bytes


def parse_sitemap(sitemap_bytes: bytes) -> dict[str, object]:
    """Return allowed URL entries from a regular sitemap or sitemap index."""

    try:
        root = ET.fromstring(sitemap_bytes)
    except ET.ParseError as error:
        raise SitemapFormatError(f"The downloaded sitemap is not valid XML: {error}") from error

    root_name = local_name(root)
    metadata: dict[str, object] = {
        "source_sitemap": SITEMAP_URL,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Entries are unclassified sitemap candidates, not confirmed support articles.",
    }

    if root_name == "urlset":
        candidates: list[dict[str, str | None]] = []
        for entry in root:
            if local_name(entry) != "url":
                continue

            location = child_text(entry, "loc")
            if location and is_allowed_support_url(location):
                candidates.append(
                    {"loc": location, "lastmod": child_text(entry, "lastmod")}
                )

        metadata.update({"sitemap_type": "urlset", "candidates": candidates})
        return metadata

    if root_name == "sitemapindex":
        child_sitemaps: list[dict[str, str | None]] = []
        for entry in root:
            if local_name(entry) != "sitemap":
                continue

            location = child_text(entry, "loc")
            if location and is_allowed_support_url(location):
                child_sitemaps.append(
                    {"loc": location, "lastmod": child_text(entry, "lastmod")}
                )

        # Child sitemaps are reported only. This script never downloads them automatically.
        metadata.update(
            {
                "sitemap_type": "sitemapindex",
                "candidates": [],
                "child_sitemaps": child_sitemaps,
            }
        )
        return metadata

    raise SitemapFormatError(
        "Unsupported XML root element "
        f"<{root_name}>. Expected <urlset> or <sitemapindex>."
    )


def save_results(results: dict[str, object]) -> None:
    """Create the data directory if needed and safely replace this script's output file."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = OUTPUT_PATH.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary_path.replace(OUTPUT_PATH)


def main() -> int:
    """Fetch, inspect, save, and report a single sitemap."""

    try:
        results = parse_sitemap(fetch_sitemap())
        save_results(results)
    except (SitemapFetchError, SitemapFormatError) as error:
        print(f"Sitemap inspection failed: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Could not save results to {OUTPUT_PATH}: {error}", file=sys.stderr)
        return 1

    candidates = results["candidates"]
    print(f"Saved {len(candidates)} candidate URL(s) to {OUTPUT_PATH.resolve()}")

    if results["sitemap_type"] == "sitemapindex":
        child_sitemaps = results["child_sitemaps"]
        print(
            f"Sitemap index detected: {len(child_sitemaps)} allowed child sitemap URL(s) "
            "were found and were not downloaded."
        )
        for child_sitemap in child_sitemaps:
            lastmod = child_sitemap["lastmod"]
            suffix = f" (last modified: {lastmod})" if lastmod else ""
            print(f"- {child_sitemap['loc']}{suffix}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
