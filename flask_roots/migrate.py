import sqlalchemy as sa


def add_column(db, table_name, column):
    column_name = column.compile(dialect=db.dialect)
    column_type = column.type.compile(db.dialect)
    with db.connect() as con:
        con.execute(sa.text('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type)))

