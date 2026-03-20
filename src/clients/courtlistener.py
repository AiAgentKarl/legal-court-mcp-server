"""
Async HTTP-Clients für Rechts-APIs.
CourtListener (US-Gerichtsentscheidungen) und EUR-Lex (EU-Recht).
"""

import httpx
from typing import Any

# Basis-URLs
COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v4"
EURLEX_BASE = "https://eur-lex.europa.eu"

# Gemeinsame Headers
HEADERS = {
    "User-Agent": "legal-court-mcp-server/0.1.0 (coach1916@gmail.com)",
    "Accept": "application/json",
}

# Timeout-Konfiguration
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


async def search_opinions(
    query: str,
    court: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Durchsucht CourtListener-Opinions (Gerichtsentscheidungen).
    Nutzt die Search-API mit Volltextsuche.
    """
    params: dict[str, Any] = {
        "q": query,
        "type": "o",  # o = opinions
        "format": "json",
    }
    if court:
        params["court"] = court

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # CourtListener Search API v3 (stabil und gut dokumentiert)
        response = await client.get(
            "https://www.courtlistener.com/api/rest/v3/search/",
            params=params,
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])[:limit]
    return {
        "count": data.get("count", 0),
        "results": [
            {
                "case_name": r.get("caseName", ""),
                "court": r.get("court", ""),
                "court_id": r.get("court_id", ""),
                "date_filed": r.get("dateFiled", ""),
                "docket_number": r.get("docketNumber", ""),
                "citation": _extract_citation(r),
                "snippet": r.get("snippet", ""),
                "absolute_url": r.get("absolute_url", ""),
                "cluster_id": r.get("cluster_id", ""),
                "id": r.get("id", ""),
            }
            for r in results
        ],
    }


async def get_opinion_cluster(cluster_id: str) -> dict[str, Any]:
    """
    Holt Details eines Opinion-Clusters von CourtListener.
    Ein Cluster enthält alle Opinions zu einem Fall.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"{COURTLISTENER_BASE}/clusters/{cluster_id}/",
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()

    return {
        "id": data.get("id"),
        "case_name": data.get("case_name", ""),
        "case_name_full": data.get("case_name_full", ""),
        "date_filed": data.get("date_filed", ""),
        "docket": data.get("docket", ""),
        "judges": data.get("judges", ""),
        "citation_count": data.get("citation_count", 0),
        "citations": [
            {
                "volume": c.get("volume"),
                "reporter": c.get("reporter"),
                "page": c.get("page"),
                "type": c.get("type"),
            }
            for c in data.get("citations", [])
        ],
        "sub_opinions": data.get("sub_opinions", []),
        "syllabus": data.get("syllabus", ""),
        "precedential_status": data.get("precedential_status", ""),
        "source": data.get("source", ""),
        "absolute_url": data.get("absolute_url", ""),
    }


async def get_opinion_detail(opinion_id: str) -> dict[str, Any]:
    """
    Holt den vollständigen Text einer einzelnen Opinion.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"{COURTLISTENER_BASE}/opinions/{opinion_id}/",
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()

    # Text extrahieren (verschiedene Formate verfügbar)
    text = (
        data.get("plain_text")
        or data.get("html_with_citations")
        or data.get("html")
        or data.get("xml_harvard")
        or ""
    )

    # HTML-Tags grob entfernen falls nötig
    if text and "<" in text:
        import re
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()

    # Auf vernünftige Länge kürzen
    if len(text) > 5000:
        text = text[:5000] + "... [gekürzt]"

    return {
        "id": data.get("id"),
        "cluster": data.get("cluster", ""),
        "author": data.get("author_str", ""),
        "type": data.get("type", ""),
        "text_excerpt": text,
        "download_url": data.get("download_url", ""),
        "date_created": data.get("date_created", ""),
    }


async def search_by_citation(citation: str) -> dict[str, Any]:
    """
    Sucht einen Fall anhand seiner Zitierung (z.B. '410 U.S. 113').
    """
    # Citation-Lookup über die Search API
    params = {
        "q": f'citation:("{citation}")',
        "type": "o",
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            "https://www.courtlistener.com/api/rest/v3/search/",
            params=params,
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])[:5]
    return {
        "count": data.get("count", 0),
        "results": [
            {
                "case_name": r.get("caseName", ""),
                "court": r.get("court", ""),
                "date_filed": r.get("dateFiled", ""),
                "docket_number": r.get("docketNumber", ""),
                "citation": _extract_citation(r),
                "snippet": r.get("snippet", ""),
                "absolute_url": r.get("absolute_url", ""),
                "cluster_id": r.get("cluster_id", ""),
            }
            for r in results
        ],
    }


async def get_court(court_id: str) -> dict[str, Any]:
    """
    Holt Infos über ein bestimmtes Gericht.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"{COURTLISTENER_BASE}/courts/{court_id}/",
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()

    return {
        "id": data.get("id", ""),
        "full_name": data.get("full_name", ""),
        "short_name": data.get("short_name", ""),
        "citation_string": data.get("citation_string", ""),
        "url": data.get("url", ""),
        "start_date": data.get("start_date", ""),
        "end_date": data.get("end_date", ""),
        "jurisdiction": data.get("jurisdiction", ""),
        "in_use": data.get("in_use", True),
        "position": data.get("position", 0),
    }


async def search_judges(name: str) -> dict[str, Any]:
    """
    Sucht Richter nach Name über CourtListener People API.
    """
    params = {
        "q": name,
        "type": "p",  # p = people/judges
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            "https://www.courtlistener.com/api/rest/v3/search/",
            params=params,
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])[:10]
    return {
        "count": data.get("count", 0),
        "results": [
            {
                "name": r.get("name", ""),
                "court": r.get("court", ""),
                "date_start": r.get("date_start", ""),
                "date_granularity_start": r.get("date_granularity_start", ""),
                "appointer": r.get("appointer", ""),
                "political_affiliation": r.get("political_affiliation", ""),
                "dob": r.get("dob", ""),
                "absolute_url": r.get("absolute_url", ""),
                "id": r.get("id", ""),
            }
            for r in results
        ],
    }


async def search_eurlex(query: str, limit: int = 10) -> dict[str, Any]:
    """
    Durchsucht EUR-Lex nach EU-Gesetzgebung und Rechtsprechung.
    Nutzt den SPARQL-Endpunkt für strukturierte Suche.
    """
    # EUR-Lex bietet einen öffentlichen SPARQL-Endpunkt
    sparql_query = f"""
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?work ?title ?date ?type WHERE {{
        ?work cdm:work_has_expression ?expr .
        ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
        ?expr cdm:expression_title ?title .
        OPTIONAL {{ ?work cdm:work_date_document ?date . }}
        OPTIONAL {{ ?work cdm:work_has_resource-type ?type . }}
        FILTER(CONTAINS(LCASE(?title), LCASE("{_escape_sparql(query)}")))
    }}
    ORDER BY DESC(?date)
    LIMIT {limit}
    """

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(
                f"{EURLEX_BASE}/EURLex-WS/sparql",
                params={
                    "query": sparql_query,
                    "format": "application/json",
                },
                headers={
                    "User-Agent": HEADERS["User-Agent"],
                    "Accept": "application/sparql-results+json",
                },
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPStatusError, httpx.RequestError):
            # Fallback: Einfache REST-Suche
            return await _eurlex_rest_search(query, limit)

    bindings = data.get("results", {}).get("bindings", [])
    return {
        "source": "EUR-Lex SPARQL",
        "count": len(bindings),
        "results": [
            {
                "celex_uri": b.get("work", {}).get("value", ""),
                "title": b.get("title", {}).get("value", ""),
                "date": b.get("date", {}).get("value", ""),
                "type": b.get("type", {}).get("value", ""),
            }
            for b in bindings
        ],
    }


async def _eurlex_rest_search(query: str, limit: int = 10) -> dict[str, Any]:
    """
    Fallback: EUR-Lex REST-Suche über die Website-Suche.
    """
    params = {
        "text": query,
        "qid": "",
        "type": "quick",
    }

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        try:
            response = await client.get(
                f"{EURLEX_BASE}/search.html",
                params=params,
                headers={
                    "User-Agent": HEADERS["User-Agent"],
                    "Accept": "text/html",
                },
            )
            # Parsen der Ergebnis-URL und Hinweis zurückgeben
            search_url = str(response.url)
        except httpx.RequestError:
            search_url = f"{EURLEX_BASE}/search.html?text={query}"

    return {
        "source": "EUR-Lex Web Search",
        "note": "SPARQL-Endpunkt nicht erreichbar, Fallback auf Web-Suche",
        "search_url": search_url,
        "suggestion": f"Direkt suchen unter: {search_url}",
        "results": [],
    }


def _extract_citation(result: dict) -> str:
    """Extrahiert die beste verfügbare Zitierung aus einem Suchergebnis."""
    citation = result.get("citation", [])
    if isinstance(citation, list) and citation:
        return citation[0]
    if isinstance(citation, str):
        return citation
    # Fallback: Lexis/West-Zitierung zusammenbauen
    return result.get("lexisCite", "") or result.get("suitNature", "") or ""


def _escape_sparql(text: str) -> str:
    """Escaped Sonderzeichen für SPARQL-Queries."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
