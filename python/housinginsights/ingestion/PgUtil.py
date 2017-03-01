







#This class should be replaced / updated to merge functionality with tools.dbtools
#Use sqlAlchemy instead of psycopg2




import psycopg2


class PgUtil(object):
    def __init__(self, dbname='postgres', user='postgres', host='localhost', port=5432, password=''):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port

        self.connection = psycopg2.connect(dbname=self._dbname, user=self._user, host=self._host, password=self._password, port=self._port)
        self.cursor = self.connection.cursor()

    def get_cursor(self):
        return self.cursor()

    def create_table(self, table_name, columns):
        """
        Create a Postgres table based on the columns passed in
        :param columns: A dict (or named tuple) mapping the column names with a type
        """
        sql = "CREATE TABLE {} (".format(table_name)
        for k, v in columns.iteritems():
            sql += "{0} {1},".format(k.lower(), v.lower())
        sql = sql.rstrip(',')
        sql += ");"
        self.cursor.execute(sql)
        self.cursor.close()
        self.connection.commit()


if __name__ == '__main__':
    print("PgUtil Class")
    pgutil = PgUtil()
    columns = {
        "apple": "VARCHAR(55)",
        "banana": "int"
    }
    pgutil.create_table('fruits', columns)