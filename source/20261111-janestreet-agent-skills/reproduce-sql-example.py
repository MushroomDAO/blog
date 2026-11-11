"""Run our teaching example. This does not evaluate an LLM or the upstream skill."""
import sqlite3,json
c=sqlite3.connect(':memory:')
c.executescript('CREATE TABLE customers(id INTEGER); CREATE TABLE orders(customer_id INTEGER); INSERT INTO customers VALUES (1),(2),(3); INSERT INTO orders VALUES (1),(NULL);')
queries={
'not_in':'SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders) ORDER BY id',
'not_exists':'SELECT id FROM customers AS c WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id=c.id) ORDER BY id',
'filtered_not_in':'SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL) ORDER BY id'}
r={'scope':'SQLite engine verification of an author-designed example, not a skill/LLM efficacy test','sqliteVersion':sqlite3.sqlite_version,'results':{k:[x[0] for x in c.execute(q)] for k,q in queries.items()},'queries':queries}
assert r['results']=={'not_in':[],'not_exists':[2,3],'filtered_not_in':[2,3]}
print(json.dumps(r,indent=2))
