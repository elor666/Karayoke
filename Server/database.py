import pathlib
import sqlite3


class DataBase():
  def __init__(self):
    if not pathlib.Path("data.db").exists():
      f = open("data.db","w") 
      f.close()

      self.conn = sqlite3.connect('data.db',check_same_thread=False)
      self.cur = self.conn.cursor()


      sql = "CREATE TABLE DATA (User TEXT UNIQUE,Password TEXT);"

      self.cur.execute(sql)
      self.close()
      
  
  def open(self):
    self.conn = sqlite3.connect('data.db')
    self.cur = self.conn.cursor()
  
  def close(self):
    self.conn.close()
  
  def login(self,username, password):
    self.open()
    sql = f"SELECT Password FROM DATA WHERE User='{username}' AND Password='{password}'"
    result = self.cur.execute(sql).fetchall()
    self.close()
    #print(result)
    if (password,) in result:
      return True
    
    return False
  
  def register(self,username, password):
    self.open()
    try:
      sql = "INSERT INTO DATA (User,Password)"
      sql += f"VALUES('{username}','{password}');"
      self.cur.execute(sql)
      self.conn.commit()
      self.close()
      return True
    except sqlite3.IntegrityError:
      self.close()
      return False

"""d = DataBase()
print(d.login("Nativ","Homo"))
print(d.register("Nativ1","Homo"))
print(d.login("p","p"))"""

