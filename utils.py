import time
import pymysql
def get_time():
    time_str=time.strftime("%Y{}%m{}%d{} %X")
    return time_str.format("年","月","日")

def get_conn():
    conn=pymysql.connect(host="127.0.0.1",
                         user="root",
                         password="417020",
                         db="db",
                         charset="utf8")
    cursor=conn.cursor()
    return conn,cursor

def close_conn(conn,cursor):
    cursor.close()
    conn.close()

def query(sql,*args):
    conn,cursor=get_conn()
    cursor.execute(sql,args)
    res=cursor.fetchall()
    close_conn(conn,cursor)
    return res

def get_c1_data():
    sql="select sum(confirm)," \
        "(select suspect from history order by ds desc limit 1)," \
        "sum(heal)," \
        "sum(dead) " \
        "from details " \
        "where update_time=(select update_time from details order by update_time desc limit 1)"
    res=query(sql)
    return res[0]
def get_c2_data():
    sql = "select province,sum(confirm) from details "\
          "where update_time=(select update_time from details "\
          "order by update_time desc limit 1) "\
          "group by province"
    res=query(sql)
    return res
	
def get_l1_data():
    sql="select ds,confirm,suspect,heal,dead from history"
    res = query(sql)
    return res
	
def get_l2_data():
    sql="select ds,confirm_add,suspect_add from history"
    res = query(sql)
    return res
	
def get_r1_data():
    sql='SELECT city,confirm FROM '\
	    '(select city,confirm from details '\
		'where update_time=(select update_time from details order by update_time desc limit 1) '\
		'and province not in ("湖北","北京","上海","天津","重庆") '\
		'union all '\
		'select province as city,sum(confirm) as confirm from details '\
		'where update_time=(select update_time from details order by update_time desc limit 1) '\
		'and province in ("北京","上海","天津","重庆") group by province) as a '\
		'ORDER BY confirm DESC LIMIT 5'
    res = query(sql)
    return res

def get_r2_data():
    sql='SELECT city,confirm FROM '\
	    '(select city,confirm from details '\
		'where update_time=(select update_time from details order by update_time desc limit 1) '\
		'and province  in ("湖北") '\
		'union all '\
		'select province as city,sum(confirm) as confirm from details '\
		'where update_time=(select update_time from details order by update_time desc limit 1) '\
		'and province in ("北京","上海","天津") group by province) as a '\
		'ORDER BY confirm DESC LIMIT 5'
    res = query(sql)
    return res
	
if __name__=="__main__":

    print(get_r1_data())
    print(get_l1_data())
    print(get_l2_data())
