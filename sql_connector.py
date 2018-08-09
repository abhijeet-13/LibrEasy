import MySQLdb

# Use this connector to make SQL queries with MySQL
class sql_connector:
    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'l', 'dblibrary')
        self.cursor = self.db.cursor()
    
    
    def run(self, query, ignore_error=True):
        try:
            self.cursor.execute(query)
            self.db.commit()
            return 0
        except Exception as e:
            if ignore_error:
                return -1
            else:
                print ('Error is: ', str(e))
                raise e

    
    def getall(self):
        return self.cursor.fetchall()
    
    def getone(self):
        return self.cursor.fetchone()
        
    def end(self):
        self.db.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, v2, v3, v4):
        self.db.close()