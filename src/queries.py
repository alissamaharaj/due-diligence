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

def last_completed(conn):
    """Get the most recent completion date for each serviced procedure.

    Takes an open connection. Returns a list of (procedure_id, last_done)
    tuples ordered by procedure_id, where last_done is the latest
    date_completed as an ISO string. Procedures with no history rows are
    not included, so the list has fewer entries than the Procedures table.
    """
    cur = conn.cursor()

    sql = '''
    SELECT procedure_id, MAX(date_completed) as last_done
    FROM Service_History
    GROUP BY procedure_id
    ORDER BY procedure_id
    '''
    rows = cur.execute(sql).fetchall()
    return rows
