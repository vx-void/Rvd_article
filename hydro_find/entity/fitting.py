from hydro_find.entity.entity import Entity

class Fitting():
    def __init__(self, query,
                 standard: str = None,
                 thread: str = None,
                 Dy: str = None,
                 angle: int = 0,
                 armature: str = 'штуцер',
                 ):
        self.query = query
        self.component = 'fittings'
        self.standard = standard
        self.thread = thread
        self.Dy = Dy
        self.angle = angle
        self.armature = armature
        # Необязательные параметры:
        self.seria = None
        self.d_out = None
        self.s_key = None
        self.usit = False
        self.o_ring = False

    def seria(self, seria: str):
        self.seria = seria

    def D_out(self, d_out: int):
        self.d_out = d_out

    def usit(self, usit: bool):
        self.usit = usit

    def o_ring(self, o_ring:bool):
        self.o_ring = o_ring

    def s_key(self, s_key: str):
        self.s_key = s_key

    def get_query(self):
        sql_query = 'SELECT name, article FROM ' + self.component + ' WHERE '
        sql_query = sql_query + (f'standard LIKE \'{self.standard}\' AND thread = \'{self.thread}\' AND '
                                 f'\"Dy\" = {self.Dy} AND angle = {self.angle} AND armature LIKE \'{self.armature}\'')
        if self.seria is not None:
            sql_query = sql_query + f' AND seria LIKE \'{self.seria}\''
        if self.d_out is not None:
            sql_query = sql_query + f' AND D_out = {self.d_out}'
        if self.usit is True:
            sql_query = sql_query + ' AND usit IS TRUE'
        if self.o_ring is True:
            sql_query = sql_query + ' AND o_ring IS TRUE'
        if self.s_key is not None:
            sql_query = sql_query + f' AND s_key = %{self.s_key()}%'

        return  sql_query

if __name__ == '__main__':
    fiting = Fitting('Фитинг BSP для РВД 3/4" прямой - 10 шт',
                     standard='BSP',
                     thread='3/4',
                     Dy=20
                     )
    print(fiting.get_query())