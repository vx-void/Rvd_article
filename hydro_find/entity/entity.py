class Entity:
    def __init__(self, query):
        self.query = query
        self.sql_query = sql_query = 'SELECT name, article FROM '
