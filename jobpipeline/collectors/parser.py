from __future__ import annotations

from bs4 import BeautifulSoup
import json


def parse_job_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {
        "title": "",
        "company": "",
        "location_text": "",
        "posted_date": None,
        "description_raw": soup.get_text(" ", strip=True)[:20000],
        "apply_url": None,
    }
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            obj = json.loads(script.text)
            if isinstance(obj, list):
                obj = next((x for x in obj if x.get("@type") == "JobPosting"), {})
            if obj.get("@type") == "JobPosting":
                result["title"] = obj.get("title", result["title"])
                result["company"] = (obj.get("hiringOrganization") or {}).get("name", result["company"])
                result["location_text"] = str(obj.get("jobLocation", result["location_text"]))
                result["posted_date"] = obj.get("datePosted")
                result["apply_url"] = obj.get("url")
                return result
        except Exception:
            continue
    # ATS hints
    text = soup.get_text(" ", strip=True).lower()
    if "greenhouse" in text:
        result["ats_type"] = "greenhouse"
    elif "lever" in text:
        result["ats_type"] = "lever"
    elif "ashby" in text:
        result["ats_type"] = "ashby"
    elif "workable" in text:
        result["ats_type"] = "workable"
    elif "workday" in text:
        result["ats_type"] = "workday"
    else:
        result["ats_type"] = "unknown"
    return result
