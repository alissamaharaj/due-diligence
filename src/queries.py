def count_by_type(conn):
    cur = conn.cursor()

    sql = ('''
    SELECT type, COUNT(*) FROM Assets 
    GROUP BY type 
    ORDER BY COUNT(*) DESC, type
    ''')
    rows = cur.execute(sql).fetchall()
    return rows
# returns list of (type,count) tuples