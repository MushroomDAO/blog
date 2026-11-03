"""Synthetic SQL semantics demonstration; not Auto Ontology/NIM benchmark."""
import sqlite3,json
c=sqlite3.connect(':memory:')
c.executescript('''CREATE TABLE orders(id INTEGER PRIMARY KEY,gross INTEGER,refund INTEGER);
CREATE TABLE items(id INTEGER PRIMARY KEY,order_id INTEGER);
INSERT INTO orders VALUES(1,100,20),(2,100,0);
INSERT INTO items VALUES(1,1),(2,1),(3,2);''')
queries={'correct_order_grain':'SELECT SUM(gross-refund) FROM orders','incorrect_fanout':'SELECT SUM(o.gross-o.refund) FROM orders o JOIN items i ON i.order_id=o.id','gross_correct':'SELECT SUM(gross) FROM orders','gross_sum_distinct_wrong':'SELECT SUM(DISTINCT gross) FROM orders'}
r={k:c.execute(q).fetchone()[0] for k,q in queries.items()};assert r=={'correct_order_grain':180,'incorrect_fanout':260,'gross_correct':200,'gross_sum_distinct_wrong':100}
print(json.dumps({'results':r,'queries':queries,'scope':'SyntheticSQLiteexample; no product query generation, model call, enterprise data or benchmark score'},indent=2))
