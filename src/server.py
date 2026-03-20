"""
Legal Court MCP Server — Rechtsrecherche für AI-Agents.
Zugriff auf 3M+ US-Gerichtsentscheidungen (CourtListener) und EU-Recht (EUR-Lex).
"""

from mcp.server.fastmcp import FastMCP
from src.tools.legal import register_tools

mcp = FastMCP(
    "Legal Court MCP Server",
    instructions=(
        "Rechtsrecherche-Server mit Zugriff auf US-Gerichtsentscheidungen "
        "(CourtListener, 3M+ Fälle) und EU-Recht (EUR-Lex). "
        "Durchsuche Fälle nach Stichwörtern, finde Details zu Urteilen, "
        "suche nach Zitierungen, Gerichten und Richtern. "
        "Ideal für juristische Recherche, Case-Law-Analyse und Rechtsvergleichung."
    ),
)

# Alle Tools registrieren
register_tools(mcp)


def main():
    """Startet den MCP-Server über stdio-Transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
