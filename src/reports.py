from pathlib import Path
import xlsxwriter
from xlsxwriter import chart
from xlsxwriter import worksheet
from xlsxwriter import workbook
from queries import overdue_by_location, overdue_by_type

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / 'reports'


def write_overdue_by_location(conn, today, path):
    """Write the overdue-by-location report to an Excel workbook.

    Takes an open connection, a 'today' date string (YYYY-MM-DD) and the
    path of the .xlsx file to create. Writes one sheet, 'Overdue by Location',
    with a bold header row (frozen), one row per location showing overdue
    procedures with history, overdue never serviced and a Total Overdue
    formula, and a bold Total row of SUM formulas. Adds a stacked column
    chart of with-history vs never-serviced counts by location, placed to
    the right of the data. Creates the reports folder if it does not exist;
    the folder of 'path' must already exist. Returns nothing.
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

    chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
    chart.add_series({
        'name': ['Overdue by Location', 0, 1],
        'categories': ['Overdue by Location', 1, 0, len(rows), 0],
        'values': ['Overdue by Location', 1, 1, len(rows), 1],
    })
    chart.add_series({
        'name': ['Overdue by Location', 0, 2],
        'categories': ['Overdue by Location', 1, 0, len(rows), 0],
        'values': ['Overdue by Location', 1, 2, len(rows), 2],
    })
    chart.set_title({'name': 'Overdue Procedures by Location'})
    chart.set_x_axis({'name': 'Location'})
    chart.set_y_axis({'name': 'Overdue procedures'})
    worksheet.insert_chart('F2', chart)

    workbook.close()

def write_overdue_by_type(conn, today, path):
    """Write the overdue-by-type report to an Excel workbook.

    Takes an open connection, a 'today' date string (YYYY-MM-DD) and the
    path of the .xlsx file to create. Writes one sheet, 'Overdue by Type',
    with a bold header row (frozen), one row per type showing overdue
    procedures with history, overdue never serviced and a Total Overdue
    formula, and a bold Total row of SUM formulas. Adds a stacked column
    chart of with-history vs never-serviced counts by type, placed to
    the right of the data. Creates the reports folder if it does not exist;
    the folder of 'path' must already exist. Returns nothing.
    """

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rows = overdue_by_type(conn, today)
    workbook = xlsxwriter.Workbook(path)
    bold = workbook.add_format({'bold': True})
    worksheet = workbook.add_worksheet('Overdue by Type')
    worksheet.set_column(0, 0, 18)
    worksheet.set_column(1, 3, 24)
    worksheet.freeze_panes(1, 0)
    worksheet.write(0, 0, 'Type', bold)
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

    chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
    chart.add_series({
        'name': ['Overdue by Type', 0, 1],
        'categories': ['Overdue by Type', 1, 0, len(rows), 0],
        'values': ['Overdue by Type', 1, 1, len(rows), 1],
    })
    chart.add_series({
        'name': ['Overdue by Type', 0, 2],
        'categories': ['Overdue by Type', 1, 0, len(rows), 0],
        'values': ['Overdue by Type', 1, 2, len(rows), 2],
    })
    chart.set_title({'name': 'Overdue Procedures by Type'})
    chart.set_x_axis({'name': 'Type'})
    chart.set_y_axis({'name': 'Overdue procedures'})
    worksheet.insert_chart('F2', chart)

    workbook.close()
