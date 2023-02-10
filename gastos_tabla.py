import sqlite3

conn = sqlite3.connect("gastos6.db")

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS gastos
(id INTEGER PRIMARY KEY AUTOINCREMENT,
fecha DATE,
descripcion TEXT,
categoria TEXT,
precio REAL
)""")


cur.execute("""CREATE TRIGGER IF NOT EXISTS actualizar_ids
AFTER DELETE ON gastos
BEGIN
    UPDATE gastos
    SET id = id - 1
    WHERE id > old.id;

    UPDATE sqlite_sequence
    SET seq = seq - 1
    WHERE name = 'gastos';
END;""")

conn.commit()
conn.close()