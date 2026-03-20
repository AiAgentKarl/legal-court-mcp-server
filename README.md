# Legal Court MCP Server

MCP Server for court decisions, case law, and legal research. Gives AI agents access to **3M+ US court decisions** via CourtListener and **EU legislation** via EUR-Lex.

## Tools

| Tool | Description |
|------|-------------|
| `search_cases` | Search 3M+ US court decisions by keyword |
| `get_case_details` | Get full case details (judges, citations, opinion text) |
| `search_by_citation` | Find a case by legal citation (e.g. "410 U.S. 113") |
| `get_court_info` | Information about a specific court |
| `search_judges` | Search judges by name |
| `search_eu_law` | Search EU legislation and case law via EUR-Lex |

## Installation

```bash
pip install legal-court-mcp-server
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "legal-court": {
      "command": "legal-court-server"
    }
  }
}
```

Or with uvx (no install needed):

```json
{
  "mcpServers": {
    "legal-court": {
      "command": "uvx",
      "args": ["legal-court-mcp-server"]
    }
  }
}
```

## Data Sources

- **CourtListener** — Free, open database of 3M+ US court opinions. No API key needed.
- **EUR-Lex** — Official EU law database with regulations, directives, and case law.

## Examples

```
search_cases("free speech first amendment")
search_cases("copyright fair use", court="scotus")
search_by_citation("347 U.S. 483")  # Brown v. Board of Education
get_court_info("scotus")
search_judges("Ruth Bader Ginsburg")
search_eu_law("artificial intelligence regulation")
```

## License

MIT
