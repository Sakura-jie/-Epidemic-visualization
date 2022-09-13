import requests
import json
import time
import pymysql
import traceback

def get_details():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=jQuery34102848205531413024_1584924641755&_=1584924641756'
    headers ={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400'
        }
    res = requests.get(url,headers=headers)
        #输出全部信息
        # print(res.text)
    response_data = json.loads(res.text.replace('jQuery34102848205531413024_1584924641755(','')[:-1])
    #输出这个字典的键值 dict_keys(['ret', 'data'])ret是响应值，0代表请求成功，data里是我们需要的数据
#     print(response_data.keys())
    """上面已经转化过一次字典，然后获取里面的data，因为data是字符串，所以需要再次转化字典
        print(json.loads(reponse_data['data']).keys())
        结果：
        dict_keys(['lastUpdateTime', 'chinaTotal', 'chinaAdd', 'isShowAdd', 'showAddSwitch',
        'areaTree', 'chinaDayList', 'chinaDayAddList', 'dailyNewAddHistory', 'dailyHistory',
        'wuhanDayList', 'articleList'])
        lastUpdateTime是最新更新时间，chinaTotal是全国疫情总数，chinaAdd是全国新增数据，
        isShowAdd代表是否展示新增数据，showAddSwitch是显示哪些数据，areaTree中有全国疫情数据
    """
    areaTree_data = json.loads(response_data['data'])['areaTree']
    temp=json.loads(response_data['data'])
#     print(temp.keys())
#     print(areaTree_data[0].keys())
    """
    获取上一级字典里的areaTree
    然后查看里面中国键值
    print(areaTree_data[0].keys())
    dict_keys(['name', 'today', 'total', 'children'])
    name代表国家名称，today代表今日数据，total代表总数,children里有全国各地数据，我们需要获取全国各地数据，查看children数据
    print(areaTree_data[0]['children'])
    这里面是
    name是地区名称，today是今日数据，total是总数，children是市级数据，
    我们通过这个接口可以获取每个地区的总数据。我们遍历这个列表，取出name，这个是省级的数据，还需要获取市级数据，
    需要取出name，children（市级数据）下的name、total(历史总数)下的confirm、heal、dead，today(今日数据)下的confirm（增加数），
    这些就是我们需要的数据
    """
        # print(areaTree_data[0]['children'])
    #     for province_data in areaTree_data[0]['children']:
        #     print(province_data)

    ds= temp['lastUpdateTime']
    details=[]
    for pro_infos in areaTree_data[0]['children']:
        province_name = pro_infos['name']  # 省名
        for city_infos in pro_infos['children']:
            city_name = city_infos['name']  # 市名
            confirm = city_infos['total']['confirm']#历史总数
            confirm_add = city_infos['today']['confirm']#今日增加数
            heal = city_infos['total']['heal']#治愈
            dead = city_infos['total']['dead']#死亡
#             print(ds,province_name,city_name,confirm,confirm_add,heal,dead)
            details.append([ds,province_name,city_name,confirm,confirm_add,heal,dead])
    return details

def get_history():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other&callback=jQuery341026745307075030955_1584946267054&_=1584946267055'
    headers ={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400'
    }
    res = requests.get(url,headers=headers)
#     print(res.text)
    response_data = json.loads(res.text.replace('jQuery341026745307075030955_1584946267054(','')[:-1])
#     print(response_data)
    data = json.loads(response_data['data'])
#     print(data.keys())
    chinaDayList = data['chinaDayList']#历史记录
    chinaDayAddList = data['chinaDayAddList']#历史新增记录
    history = {}
    for i in chinaDayList:
        ds = '2021.' + i['date']#时间
        tup = time.strptime(ds,'%Y.%m.%d')
        ds = time.strftime('%Y-%m-%d',tup)#改变时间格式，插入数据库
        confirm = i['confirm']
        suspect = i['suspect']
        heal = i['heal']
        dead = i['dead']
        history[ds] = {'confirm':confirm,'suspect':suspect,'heal':heal,'dead':dead}
    for i in chinaDayAddList:
        ds = '2021.' + i['date']#时间
        tup = time.strptime(ds,'%Y.%m.%d')
        ds = time.strftime('%Y-%m-%d',tup)#改变时间格式，插入数据库
        confirm_add = i['confirm']
        suspect_add = i['suspect']
        heal_add = i['heal']
        dead_add = i['dead']
        history[ds].update({'confirm_add':confirm_add,'suspect_add':suspect_add,'heal_add':heal_add,'dead_add':dead_add})
    return history

def get_conn():
    """
    :return: 连接，游标
    """
    # 创建连接
    conn = pymysql.connect(host="127.0.0.1",
                    user="root",
                    password="417020",
                    db="db",
                    charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor
def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def update_details():
    """
    更新 details 表
    :return:
    """
    cursor = None
    conn = None
    try:
        li = get_details()
        conn, cursor = get_conn()
        sql = "insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
        sql_query = 'select %s=(select update_time from details order by id desc limit 1)' #对比当前最大时间戳
        cursor.execute(sql_query,li[0][0])
        if not cursor.fetchone()[0]:
            print(f"{time.asctime()}开始更新最新数据")
            for item in li:
                cursor.execute(sql, item)
            conn.commit()  # 提交事务 update delete insert操作
            print(f"{time.asctime()}更新最新数据完毕")
        else:
            print(f"{time.asctime()}已是最新数据！")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

        def insert_history():
            """
                插入历史数据
            :return:
            """
            cursor = None
            conn = None
            try:
                dic = get_history()
                print(f"{time.asctime()}开始插入历史数据")
                conn, cursor = get_conn()
                sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                for k, v in dic.items():
                    # item 格式 {'2021-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
                    cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                         v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                         v.get("dead"), v.get("dead_add")])

                conn.commit()  # 提交事务 update delete insert操作
                print(f"{time.asctime()}插入历史数据完毕")
            except:
                traceback.print_exc()
            finally:
                close_conn(conn, cursor)

def insert_history():
    """
        插入历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dic = get_history()
        print(f"{time.asctime()}开始插入历史数据")
        conn, cursor = get_conn()
        sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for k, v in dic.items():
            # item 格式 {'2021-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
            cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                 v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                 v.get("dead"), v.get("dead_add")])

        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}插入历史数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def update_history():
    """
    更新历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dic = get_history()
        print(f"{time.asctime()}开始更新历史数据")
        conn, cursor = get_conn()
        sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql_query = "select confirm from history where ds=%s"
        for k, v in dic.items():
            # item 格式 {'2020-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
            if not cursor.execute(sql_query, k):
                cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                     v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                     v.get("dead"), v.get("dead_add")])
        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}历史数据更新完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

update_history()
insert_history()
update_details()


