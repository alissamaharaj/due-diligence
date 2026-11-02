def count_by_type(conn):
    """Count assets per type.

    Takes an open connection. Returns a list of (type, count) tuples,
    ordered by count descending, then type alphabetically.
    """
    cur = conn.cursor()

    sql = '''
    SELECT type, COUNT(*) FROM Assets 
    GROUP BY type 
    ORDER BY COUNT(*) DESC, type
    '''
    rows = cur.execute(sql).fetchall()
    return rows

def history_for_procedure(conn, proc_id):
    """Get the service history for one procedure.

    Takes an open connection and a procedure id such as 'PMP-002-P1'.
    Returns a list of (record_id, date_completed, notes) tuples, oldest
    first. notes is None when no note was recorded. Returns an empty list
    if the procedure has no history or does not exist.
    """
    cur = conn.cursor()

    sql = '''
    SELECT record_id, date_completed, notes FROM Service_History
    WHERE procedure_id = ?
    ORDER BY date_completed
    '''
    rows = cur.execute(sql, (proc_id,)).fetchall()
    return rows

def linked_partner(conn, asset_id):
    """Get the asset linked to one given asset.

    Takes an open connection and an asset id such as 'PMP-001'. Returns a
    list of (a_id, a_type, b_id, b_type) tuples, where a is the asset
    passed in and b is its partner. Returns one row for a linked asset and
    an empty list if the asset has no link or does not exist.
    """
    cur = conn.cursor()

    sql = '''
    SELECT a.asset_id, a.type, b.asset_id, b.type 
    FROM Assets as a
    JOIN Assets as b
    ON a.linked_asset_id = b.asset_id
    WHERE a.asset_id = ?
    '''
    rows = cur.execute(sql, (asset_id,)).fetchall()
    return rows

def linked_pairs(conn):
    """List every linked pair once.

    Takes an open connection. Returns a list of (a_id, a_type, b_id, b_type)
    tuples ordered by a_id. Links are stored on both sides, so
    a.asset_id < b.asset_id keeps only one direction per pair. The asset
    whose id sorts first appears on the left (MTR before PMP).
    """
    cur = conn.cursor()

    sql = '''
    SELECT a.asset_id, a.type, b.asset_id, b.type 
    FROM Assets as a
    JOIN Assets as b
    ON a.linked_asset_id = b.asset_id
    WHERE a.asset_id < b.asset_id
    ORDER BY a.asset_id
    '''
    rows = cur.execute(sql).fetchall()
    return rows

def last_completed_all(conn):
    """Get the most recent completion date for every procedure.

    Takes an open connection. Returns a list of (procedure_id, last_done)
    tuples for all procedures, ordered by procedure_id. last_done is the
    latest date_completed as an ISO string, or None if the procedure has
    never been serviced (no history rows).
    """
    cur = conn.cursor()

    sql = '''
    SELECT p.procedure_id, h.last_done
    FROM Procedures as p
    LEFT JOIN  ( 
        SELECT procedure_id, MAX(date_completed)
    AS last_done
        FROM Service_History
        GROUP BY procedure_id
    ) as h
    ON p.procedure_id = h.procedure_id
    ORDER BY p.procedure_id
    '''
    rows = cur.execute(sql).fetchall()
    return rows

def procedure_due_dates(conn):

    cur = conn.cursor()

    sql = '''
    SELECT p.procedure_id, h.last_done, a.commissioning_date, f.service_interval_days, date(COALESCE(h.last_done, a.commissioning_date),'+' || f.service_interval_days || ' days') AS next_due
    FROM Procedures as p
    LEFT JOIN  ( 
        SELECT procedure_id, MAX(date_completed) AS last_done
        FROM Service_History
        GROUP BY procedure_id
    ) as h
    ON p.procedure_id = h.procedure_id
    JOIN Assets AS a ON p.asset_id = a.asset_id
    JOIN Frequencies AS f ON p.service_frequency = f.service_frequency
    ORDER BY p.procedure_id
    '''
    rows = cur.execute(sql).fetchall()
    return rows
