"""
MCP-Tools für Rechtsrecherche.
Stellt CourtListener- und EUR-Lex-Daten als MCP-Tools bereit.
"""

from mcp.server.fastmcp import FastMCP
from src.clients import courtlistener


def register_tools(mcp: FastMCP) -> None:
    """Registriert alle Legal-Tools am MCP-Server."""

    @mcp.tool()
    async def search_cases(
        query: str,
        court: str | None = None,
        limit: int = 10,
    ) -> dict:
        """
        Durchsucht 3M+ US-Gerichtsentscheidungen nach Stichwörtern.

        Args:
            query: Suchbegriff(e), z.B. 'free speech first amendment'
            court: Optional — Gericht filtern, z.B. 'scotus' (Supreme Court),
                   'ca1' bis 'ca11' (Circuit Courts), 'dcd' (DC District)
            limit: Maximale Anzahl Ergebnisse (Standard: 10, Max: 20)

        Returns:
            Gefundene Fälle mit Name, Gericht, Datum, Zitierung und Textausschnitt.

        Beispiele:
            search_cases('copyright fair use')
            search_cases('miranda rights', court='scotus')
            search_cases('data privacy GDPR', limit=5)
        """
        limit = min(max(1, limit), 20)

        try:
            return await courtlistener.search_opinions(query, court, limit)
        except Exception as e:
            return {"error": f"Suche fehlgeschlagen: {str(e)}"}

    @mcp.tool()
    async def get_case_details(case_id: str) -> dict:
        """
        Holt vollständige Details eines Falls von CourtListener.

        Args:
            case_id: Die Cluster-ID oder Opinion-ID des Falls.
                     Erhält man aus search_cases (cluster_id oder id Feld).

        Returns:
            Vollständige Falldetails: Name, Richter, Zitierungen,
            Präzedenzstatus und Textausschnitt der Entscheidung.

        Beispiele:
            get_case_details('2812209')  # Cluster-ID
        """
        try:
            # Erst Cluster-Details holen
            cluster = await courtlistener.get_opinion_cluster(case_id)

            # Wenn Sub-Opinions vorhanden, erste Opinion holen
            opinion_text = ""
            sub_opinions = cluster.get("sub_opinions", [])
            if sub_opinions:
                # Opinion-ID aus URL extrahieren
                first_opinion_url = sub_opinions[0] if isinstance(sub_opinions[0], str) else ""
                if first_opinion_url:
                    opinion_id = first_opinion_url.rstrip("/").split("/")[-1]
                    try:
                        opinion = await courtlistener.get_opinion_detail(opinion_id)
                        opinion_text = opinion.get("text_excerpt", "")
                    except Exception:
                        pass  # Opinion-Text ist optional

            cluster["opinion_excerpt"] = opinion_text
            return cluster

        except Exception as e:
            return {"error": f"Falldetails konnten nicht geladen werden: {str(e)}"}

    @mcp.tool()
    async def search_by_citation(citation: str) -> dict:
        """
        Findet einen Fall anhand seiner juristischen Zitierung.

        Args:
            citation: Die Zitierung, z.B. '410 U.S. 113' (Roe v. Wade),
                      '347 U.S. 483' (Brown v. Board of Education),
                      '384 U.S. 436' (Miranda v. Arizona)

        Returns:
            Passende Fälle mit vollständigen Metadaten.

        Beispiele:
            search_by_citation('410 U.S. 113')
            search_by_citation('554 U.S. 570')
        """
        try:
            return await courtlistener.search_by_citation(citation)
        except Exception as e:
            return {"error": f"Zitierungs-Suche fehlgeschlagen: {str(e)}"}

    @mcp.tool()
    async def get_court_info(court_id: str) -> dict:
        """
        Holt Informationen über ein bestimmtes Gericht.

        Args:
            court_id: Die Court-ID, z.B.:
                      'scotus' — US Supreme Court
                      'ca1' bis 'ca11' — US Circuit Courts
                      'cafc' — Federal Circuit
                      'cadc' — DC Circuit
                      'dcd' — DC District Court
                      'nyed', 'nysd' — NY District Courts

        Returns:
            Gerichtsname, Jurisdiktion, Gründungsdatum und Status.

        Beispiele:
            get_court_info('scotus')
            get_court_info('ca9')
        """
        try:
            return await courtlistener.get_court(court_id)
        except Exception as e:
            return {"error": f"Gerichts-Info nicht verfügbar: {str(e)}"}

    @mcp.tool()
    async def search_judges(name: str) -> dict:
        """
        Sucht Richter nach Name und zeigt deren Informationen.

        Args:
            name: Name des Richters, z.B. 'Ruth Bader Ginsburg',
                  'John Roberts', 'Sonia Sotomayor'

        Returns:
            Richter-Informationen: Name, Gericht, Ernennung,
            politische Zugehörigkeit.

        Beispiele:
            search_judges('Ketanji Brown Jackson')
            search_judges('Clarence Thomas')
        """
        try:
            return await courtlistener.search_judges(name)
        except Exception as e:
            return {"error": f"Richter-Suche fehlgeschlagen: {str(e)}"}

    @mcp.tool()
    async def search_eu_law(query: str, limit: int = 10) -> dict:
        """
        Durchsucht EU-Recht und Rechtsprechung über EUR-Lex.

        Args:
            query: Suchbegriff(e) auf Englisch, z.B. 'data protection',
                   'consumer rights', 'competition law'
            limit: Maximale Anzahl Ergebnisse (Standard: 10, Max: 20)

        Returns:
            EU-Rechtsakte und Urteile mit Titel, CELEX-Nummer und Datum.

        Beispiele:
            search_eu_law('artificial intelligence regulation')
            search_eu_law('GDPR data protection', limit=5)
        """
        limit = min(max(1, limit), 20)

        try:
            return await courtlistener.search_eurlex(query, limit)
        except Exception as e:
            return {"error": f"EUR-Lex-Suche fehlgeschlagen: {str(e)}"}
