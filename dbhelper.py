import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text, priority text)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        priorityidx = "CREATE INDEX IF NOT EXISTS priorityIndex ON items (priority ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.execute(priorityidx)
        self.conn.commit()

    def add_item(self, item_text, owner, priority):
        stmt = "INSERT INTO items (description, owner, priority) VALUES (?, ?, ?)"
        args = (item_text, owner, priority)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, owner):
        stmt = "SELECT description, priority FROM items WHERE owner = (?)"
        args = (owner, )
        return [(x[0], x[1]) for x in self.conn.execute(stmt, args)]