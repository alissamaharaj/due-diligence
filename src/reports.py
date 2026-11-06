from pathlib import Path
import xlsxwriter
from queries import overdue_by_location

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / 'reports'


def write_overdue_by_location(conn, today, path):
    """Write the overdue-by-location report to an Excel workbook.

    Takes an open connection, today as an ISO date string (YYYY-MM-DD),
    and the output path for the .xlsx file. Writes one sheet with a header
    row and one row per location with at least one overdue procedure:
    location, overdue with history, overdue never serviced, and a total
    overdue column (a formula adding the two counts). Rows follow the order
    given by overdue_by_location. A final Total row sums each count column
    using SUM formulas. The header row is frozen and bold, as is the Total
    row. Creates the reports folder if it does not exist. Returns nothing.
    """

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    rows = overdue_by_location(conn, today)
    workbook = xlsxwriter.Workbook(path)
    bold = workbook.add_format({'bold': True})
    worksheet = workbook.add_worksheet('Overdue by Location')
    worksheet.set_column(0, 0, 18)
    worksheet.set_column(1, 3, 24)
    worksheet.freeze_panes(1, 0)
    worksheet.write(0, 0, 'Location', bold)
    worksheet.write(0, 1, 'Overdue (with history)', bold)
    worksheet.write(0, 2, 'Overdue (never serviced)', bold)
    worksheet.write(0, 3, 'Total Overdue', bold)
    worksheet.write(len(rows) + 1, 0, 'Total', bold)
    for i, row in enumerate(rows, start=1):
        worksheet.write(i, 0, row[0])
        worksheet.write(i, 1, row[1])
        worksheet.write(i, 2, row[2])
        worksheet.write_formula(i, 3, f'=B{i+1}+C{i+1}')
    worksheet.write_formula(len(rows) + 1, 1, f'=SUM(B2:B{len(rows)+1})', bold)
    worksheet.write_formula(len(rows) + 1, 2, f'=SUM(C2:C{len(rows)+1})', bold)
    worksheet.write_formula(len(rows) + 1, 3, f'=SUM(D2:D{len(rows)+1})', bold)
    workbook.close()
