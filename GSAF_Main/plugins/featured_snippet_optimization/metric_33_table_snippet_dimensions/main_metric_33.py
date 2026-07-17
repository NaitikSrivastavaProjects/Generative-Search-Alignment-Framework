'''
Table Snippet Dimensions Checker:
Detects whether tables have 2-4 columns and at least 3 rows — the
dimension range AI engines extract most cleanly as table snippets.
'''
from models.metric_result import MetricResult
from utils.helpers import get_status

def run(site_data):
    result = MetricResult(factor="33 - Table Snippet Dimensions")
    try:
        tables = site_data.soup.find_all("table")
        if not tables:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No tables found on page"
            return result.to_dict()

        checked = []
        good_count = 0
        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue
            first_row_cells = rows[0].find_all(["td", "th"])
            col_count = len(first_row_cells)
            row_count = len(rows)

            good_cols = 2 <= col_count <= 4
            good_rows = row_count >= 3
            is_good = good_cols and good_rows
            if is_good:
                good_count += 1
            checked.append({"columns": col_count, "rows": row_count, "in_range": is_good})

        if not checked:
            result.score = 0
            result.status = get_status(0)
            result.details["reason"] = "No valid tables found"
            return result.to_dict()

        score = round((good_count / len(checked)) * 100)
        result.score = score
        result.status = get_status(score)
        result.details["total_tables"] = len(checked)
        result.details["tables_in_range"] = good_count
        result.details["checked"] = checked

        if score < 100:
            result.recommendations.append("Structure tables with 2-4 columns and at least 3 rows for optimal snippet extraction.")

    except Exception as e:
        result.error = str(e)

    return result.to_dict()