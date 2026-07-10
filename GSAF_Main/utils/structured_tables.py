def analyze_structured_tables(site_data):

    soup = site_data.soup

    tables = soup.find_all("table")

    total_tables = len(tables)

    structured_tables = 0

    total_headers = 0

    total_rows = 0

    score = 0

    recommendations = []

    for table in tables:

        headers = table.find_all("th")

        rows = table.find_all("tr")

        if len(headers) >= 2:

            structured_tables += 1

        total_headers += len(headers)

        total_rows += len(rows)

    score += min(total_tables, 5) * 15

    score += min(structured_tables, 5) * 10

    score += min(total_headers, 10) * 2

    score += min(total_rows, 20) * 1

    score = min(score, 100)

    details = {
        "tables_found": total_tables,
        "structured_tables": structured_tables,
        "table_headers": total_headers,
        "table_rows": total_rows
    }

    if score < 75:

        if total_tables == 0:

            recommendations.append(
                "Include HTML tables for structured comparisons."
            )

        elif structured_tables == 0:

            recommendations.append(
                "Use <th> elements to create proper table headers."
            )

        if total_rows < 4:

            recommendations.append(
                "Expand comparison tables with additional comparison points."
            )

    return {
        "score": score,
        "details": details,
        "recommendations": recommendations
    }