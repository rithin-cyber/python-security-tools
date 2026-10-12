#!/usr/bin/env python3
"""Inspect common HTTP security headers for an authorized target."""

import argparse
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def has_frame_ancestors(csp):
    """Return True when CSP contains a frame-ancestors directive."""
    for directive in csp.split(";"):
        parts = directive.strip().lower().split()
        if parts and parts[0] == "frame-ancestors":
            return True
    return False


def check_headers(url):
    """Make one GET request and report selected response headers."""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print("Error: provide a complete http:// or https:// URL.")
        return 1

    request = Request(
        url,
        headers={"User-Agent": "PythonSecurityHeaderChecker/1.0"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=10) as response:
            status = response.status
            headers = response.headers
            final_url = response.geturl()
    except HTTPError as error:
        # HTTP errors can still contain useful response headers.
        status = error.code
        headers = error.headers
        final_url = error.geturl()
        error.close()
    except (URLError, TimeoutError, OSError, ValueError) as error:
        print(f"Request failed: {error}")
        return 1

    final_scheme = urlsplit(final_url).scheme
    print("\nHTTP Security Header Checker")
    print("=" * 40)
    print(f"Final URL: {final_url}")
    print(f"HTTP status: {status}")
    print("\nHeader results")
    print("-" * 40)

    hsts = headers.get("Strict-Transport-Security")
    if final_scheme != "https":
        print("HSTS: NOT EVALUATED (final URL is not HTTPS)")
    elif hsts:
        print(f"HSTS: PRESENT ({hsts})")
    else:
        print("HSTS: MISSING")

    csp = headers.get("Content-Security-Policy", "")
    print(f"CSP: {'PRESENT' if csp else 'MISSING'}")

    nosniff = headers.get("X-Content-Type-Options", "")
    if nosniff.lower().strip() == "nosniff":
        print("X-Content-Type-Options: PRESENT (nosniff)")
    elif nosniff:
        print(f"X-Content-Type-Options: CHECK VALUE ({nosniff})")
    else:
        print("X-Content-Type-Options: MISSING")

    xfo = headers.get("X-Frame-Options")
    csp_frame = has_frame_ancestors(csp)
    if xfo or csp_frame:
        protections = []
        if xfo:
            protections.append(f"X-Frame-Options: {xfo}")
        if csp_frame:
            protections.append("CSP frame-ancestors")
        print(f"Framing protection: FOUND ({'; '.join(protections)})")
    else:
        print("Framing protection: NOT DETECTED")

    for name in ("Referrer-Policy", "Permissions-Policy"):
        value = headers.get(name)
        print(f"{name}: PRESENT ({value})" if value else f"{name}: MISSING")

    print("\nInterpretation")
    print("Missing headers are observations, not automatic proof")
    print("of a vulnerability. Review the site and its requirements.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Inspect common HTTP security response headers."
    )
    parser.add_argument("url", help="Authorized HTTP or HTTPS target URL")
    args = parser.parse_args()
    return check_headers(args.url)


if __name__ == "__main__":
    sys.exit(main())
