#!/usr/bin/env python3
"""Daily no-key cybersecurity job discovery for India-eligible candidates.
Uses public feeds for personal job research. Never submits applications or emails.
"""
from __future__ import annotations
import csv
import html
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "job-search" / "data"
QUERIES = ("cybersecurity", "penetration tester", "VAPT", "application security", "security analyst")
PATTERN = re.compile(r"penetration[\s-]*test|pentest|VAPT|application[\s-]*security|appsec|cyber[\s-]*security|security[\s-]*(?:analyst|tester|researcher|consultant)|vulnerability[\s-]*(?:assess|analyst)|offensive[\s-]*security|red[\s-]*team", re.I)
SENIOR = re.compile(r"\b(senior|sr\.?|lead|principal|director|manager|staff|architect|head|chief|vp|vice president)\b", re.I)
JUNIOR = re.compile(r"\b(junior|entry[\s-]*level|associate|trainee|apprentice|intern|fresher)\b", re.I)
UNPAID = re.compile(r"\b(unpaid|volunteer|no stipend|without stipend|pay[- ]to[- ]train|pay[- ]for[- ]training)\b", re.I)
DEGREE = re.compile(r"\b(?:must|required|mandatory|minimum)\b.{0,90}\b(?:bachelor(?:'s)?|university degree|b\.?tech|b\.?e\.|b\.?sc)\b", re.I | re.S)
FIELDS = ["found_at_utc", "source", "company", "title", "location", "salary", "posted_at", "application_url", "candidate_fit", "review_needed"]
UA = "IndiaCyberJobsPersonalResearch/1.0 (+https://github.com/rithin-cyber/python-security-tools)"

def get_json(url: str) -> object:
    request = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)

def plaintext(value: object) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", str(value or "")))).strip()

def worldwide_or_india(location: str) -> bool:
    loc = location.lower()
    return not loc or any(w in loc for w in ("worldwide", "anywhere", "global", "india", "asia", "apac", "all countries"))

def acceptable(title: str, description: str, salary: str) -> bool:
    if not PATTERN.search(title) or SENIOR.search(title):
        return False
    if UNPAID.search(title + " " + description[:1200]):
        return False
    if DEGREE.search(description[:4500]):
        return False
    if re.search(r"\b(intern|internship|apprentice)\b", title, re.I):
        # A stipend or salary must be explicit before promoting an internship.
        if not (salary and salary.lower() not in ("none", "not listed", "unknown")) and not re.search(r"\b(paid internship|paid intern|stipend of|monthly stipend)\b", description[:4500], re.I):
            return False
    return True

def build(source: str, company: str, title: str, location: str, salary: str, posted: str, url: str, description: str) -> dict | None:
    title = plaintext(title)
    description = plaintext(description)
    if not url.startswith(("https://", "http://")) or not acceptable(title, description, salary):
        return None
    score = "High (junior title)" if JUNIOR.search(title) else "Review (level unspecified)"
    return {
        "found_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "company": plaintext(company)[:180],
        "title": title[:220],
        "location": plaintext(location)[:180],
        "salary": salary or "Not listed",
        "posted_at": str(posted or ""),
        "application_url": url,
        "candidate_fit": score,
        "review_needed": "Verify live opening, paid status, degree acceptance, and India eligibility before contacting",
    }

def himalayas():
    for q in QUERIES:
        url = "https://himalayas.app/jobs/api/search?q=" + quote(q) + "&country=IN&sort=recent&page=1"
        obj = get_json(url)
        for j in obj.get("jobs", []):
            restrictions = j.get("locationRestrictions") or []
            if restrictions and not any((isinstance(x, dict) and (x.get("alpha2", "").upper() == "IN" or x.get("name", "").lower() == "india")) for x in restrictions):
                continue
            lo = j.get("minSalary") or j.get("maxSalary")
            sal = (str(j.get("currency") or "") + " " + str(j.get("minSalary") or "") + "–" + str(j.get("maxSalary") or "")).strip() if lo else ""
            row = build("Himalayas", j.get("companyName", ""), j.get("title", ""), "Remote — India/worldwide", sal, j.get("pubDate", ""), j.get("applicationLink", ""), j.get("description", ""))
            if row:
                yield row
        time.sleep(1)

def remotive():
    obj = get_json("https://remotive.com/api/remote-jobs")
    for j in obj.get("jobs", []):
        loc = str(j.get("candidate_required_location") or "")
        if not worldwide_or_india(loc):
            continue
        row = build("Remotive", j.get("company_name", ""), j.get("title", ""), loc or "Remote — location unspecified", str(j.get("salary") or ""), j.get("publication_date", ""), j.get("url", ""), j.get("description", ""))
        if row:
            yield row

def remoteok():
    obj = get_json("https://remoteok.com/api")
    if not isinstance(obj, list):
        return
    for j in obj:
        if not isinstance(j, dict) or not j.get("position"):
            continue
        loc = str(j.get("location") or "")
        if not worldwide_or_india(loc):
            continue
        sal = (str(j.get("salary_min") or "") + "–" + str(j.get("salary_max") or "")).strip("–") if j.get("salary_min") or j.get("salary_max") else ""
        row = build("Remote OK", j.get("company", ""), j.get("position", ""), loc or "Remote — location unspecified", sal, j.get("date", ""), j.get("url", ""), j.get("description", ""))
        if row:
            yield row


def greenhouse():
    """Public official Greenhouse boards; no sign-in, no harvesting of contacts."""
    boards = (
        ("Dragos", "dragos"),
        ("Cobalt", "cobaltio"),
        ("Bugcrowd", "bugcrowd"),
        ("Clearwater", "clearwater"),
        ("Tenable", "tenableinc"),
        ("GuidePoint Security", "guidepointsecurity"),
        ("ConnectWise", "connectwise"),
        ("Zscaler", "zscaler"),
    )
    exclude = re.compile(r"\b(?:United States|USA|U\.S\.|US|Canada|Mexico|Costa Rica|UK|United Kingdom|London|Berlin|Germany|France|Poland|Australia|Singapore|Philippines|Brazil|Colombia|Japan|UAE|Dubai)\b", re.I)
    india = re.compile(r"\b(?:India|Bengaluru|Bangalore|Kochi|Kozhikode|Pune|Mumbai|Delhi|Gurugram|Gurgaon|Hyderabad|Chennai|Noida|Kolkata|Kerala|Ahmedabad|Chandigarh|Jaipur|Thiruvananthapuram|Worldwide|Global)\b", re.I)
    for company, board in boards:
        try:
            obj = get_json("https://boards-api.greenhouse.io/v1/boards/" + quote(board) + "/jobs?content=true")
        except Exception as exc:
            print("Greenhouse " + company + " unavailable: " + str(exc)[:100], file=sys.stderr)
            continue
        for job in obj.get("jobs", []):
            loc = str((job.get("location") or {}).get("name") or "")
            if exclude.search(loc + ' ' + str(job.get('title', ''))) or not india.search(loc):
                continue
            row = build("Greenhouse — " + company, company, job.get("title", ""), loc or "Location not listed", "", job.get("updated_at", ""), job.get("absolute_url", ""), job.get("content", ""))
            if row:
                yield row
        time.sleep(0.3)

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    old_seen_path = DATA / "seen_job_urls.json"
    old = set(json.loads(old_seen_path.read_text(encoding="utf-8"))) if old_seen_path.exists() else set()
    rows: dict[str, dict] = {}
    errors = {}
    sources_ok = 0
    for name, fn in (("Himalayas", himalayas), ("Remotive", remotive), ("Remote OK", remoteok), ("Greenhouse official boards", greenhouse)):
        try:
            for row in fn():
                rows.setdefault(row["application_url"], row)
            sources_ok += 1
        except Exception as exc:
            errors[name] = str(exc)[:240]
            print(f"Source failed ({name}): {exc}", file=sys.stderr)
    if sources_ok == 0:
        sys.exit("No source worked: preserving existing results")
    ordered = sorted(rows.values(), key=lambda x: (x["candidate_fit"].startswith("High"), x["posted_at"]), reverse=True)
    with (DATA / "india_cybersecurity_jobs.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ordered)
    (DATA / "india_cybersecurity_jobs.json").write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fresh = [x for x in ordered if x["application_url"] not in old]
    (DATA / "new_job_urls.json").write_text(json.dumps([r["application_url"] for r in fresh], indent=2) + "\n", encoding="utf-8")
    (DATA / "seen_job_urls.json").write_text(json.dumps(sorted(old | set(rows)), indent=2) + "\n", encoding="utf-8")
    summary = {"checked_utc": datetime.now(timezone.utc).isoformat(), "sources_ok": sources_ok, "matching_current_jobs": len(ordered), "first_seen_in_this_run": len(fresh), "source_errors": errors, "note": "Personal research feed, not verified applications, emails or guaranteed paid/eligible roles"}
    (DATA / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
