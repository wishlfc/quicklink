import os, sys
import MySQLdb
import multiprocessing
from multiprocessing import TimeoutError

timeout = 20
from types import MethodType, SliceType

from django.conf import settings
dbserver = settings.DATABASES['default']['HOST']
print 'Current DB Server is: ', dbserver

class dba(object):
    def __init__(self):
        from django.conf import settings
        self.ip         =   settings.DATABASES['default']['HOST']
        self.port       =   int(settings.DATABASES['default']['PORT'])
        self.username   =   settings.DATABASES['default']['USER']
        self.password   =   settings.DATABASES['default']['PASSWORD']
        self.dbname     =   settings.DATABASES['default']['NAME']
        self.db = None

    def connect(self):
        if not self.db:
            self.db = MySQLdb.connect(host=self.ip, user=self.username,
                        passwd=self.password, db=self.dbname, port=self.port, connect_timeout = 20)
            self.cursor = self.db.cursor()

    def disconnect(self):
        self.db.close()
        self.cursor = None

def query_with_timeout(dbc, timeout, query, *a, **k):
    conn1, conn2 = multiprocessing.Pipe(False)
    subproc = multiprocessing.Process(target=do_query,
                                        args=(dbc, query, conn2)+a,
                                        kwargs=k)
    subproc.start()
    subproc.join(20)
    if conn1.poll():
        return conn1.recv()
    subproc.terminate()
    raise TimeoutError("Query %r ran for >%r" % (query, str(timeout)))

def do_query(dbc, query, conn, *a, **k):
    cu = dbc.cursor()
    cu.execute(query, *a, **k)
    conn.send(cu.fetchall())
    return cu.fetchall()

# adb = dba()
# adb.connect()
# print 'Connect to DB successfully.'
# try:
#     query_with_timeout(adb.db, 10, 'select count(*) from tblusers;')
#     print 'DB is OK.'
# except:
#     raise('Database exception, check the db please.')


class IpaMmlItem:
    """ base class for items contained in CommonDict """
    def __str__(self):
        """ support a nice string representation with all attribute values"""
        tmp = "\n".join(sorted([ "      %s=%s" % (item, getattr(self, item)) for item in dir(self)
                                if not item.startswith("_") and getattr(self, item) != None and
                                    type(getattr(self, item)) is not MethodType ] ))
        for i in range(len(tmp)):
            if ord(tmp[i]) > 127:
                tmp = tmp.replace(tmp[i], " ")
        return str(self.__class__.__name__) + ':\n{\n' + tmp + '}\n'

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()


def get_data_from_sql(sql):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    adb.cursor.execute(sql)
    fields = [x[0] for x in adb.cursor.description]
    result = [record[0] for record in adb.cursor.fetchall()]
    return result

def get_data_from_sql_m(sql):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    adb.cursor.execute(sql)
    fields = [x[0] for x in adb.cursor.description]
    result = adb.cursor.fetchall()
    return query_with_timeout(adb.db,timeout,sql)

def get_data_from_sql_f(sql):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    adb.cursor.execute(sql)
    fields = [x[0] for x in adb.cursor.description]
    result = adb.cursor.fetchall()
    return fields, query_with_timeout(adb.db,timeout,sql)


def get_table_columns(tablename):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    sql = 'desc '+tablename
    adb.cursor.execute('desc '+tablename)
    return query_with_timeout(adb.db,timeout,sql)

def run_sql(sql):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    adb.cursor.execute(sql)
    adb.cursor.execute('commit;')


def get_scenario_check_fields():
    fields = get_table_columns('tblscenario')
    return [field[0] for field in fields if 'tinyint' in field[1]]


def get_user_list():
    users = get_data_from_sql('select mail from tblusers;')
    users.sort()
    return users

def get_user_aka_list():
    users = get_data_from_sql('select aka from vj_users_pet1;')
    users.sort()
    return users

def get_tm500_list():
    tm500s = get_data_from_sql('select distinct tm500id from v_tbltm500mn;')
    tm500s.sort()
    return tm500s

def get_pa_solution():
    solutions = get_data_from_sql('select distinct solution from tblrfconn where solution is not NULL order by solution;')
    solutions.sort()
    return solutions

def get_data_by_sql(sql):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    adb.cursor.execute(sql)
    fields = [x[0] for x in adb.cursor.description]
    result = []
    for row in adb.cursor.fetchall():
        item = IpaMmlItem()
        for i in range(len(fields)):
            setattr(item, fields[i], str(row[i]))
        result.append(item)
    return fields, result

def get_case_field_var(show_name):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    show_fieldname = show_name
    sql = 'select db_fieldname from tblcasedict where show_fieldname = "%s";'%(show_fieldname)
    # adb.cursor.execute(sql)
    db_fieldname = ''
    for row in query_with_timeout(adb.db,timeout,sql):
        db_fieldname = str(row[0]).replace('(','').replace(')','')
    return db_fieldname

def get_case_field_type(show_name):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    show_fieldname = show_name
    sql = 'select field_type from tblcasedict where show_fieldname = "%s";'%(show_fieldname)
    # adb.cursor.execute(sql)
    fieldtype = ''
    for row in query_with_timeout(adb.db,timeout,sql):
        fieldtype = str(row[0]).replace('(','').replace(')','')
    return fieldtype

def get_table_content(tablename = '', condition = ''):
    try:
        adb.db.ping()
    except Exception,e:
        adb = dba()
        adb.connect()
    fields = get_table_columns(tablename)
    adb.cursor.execute('select * from  %s %s;' %(tablename, condition))
    result = []
    for record in adb.cursor.fetchall():
        p = IpaMmlItem()
        for i in range(len(fields)):
            if record[i] <> None:
                setattr(p, fields[i][0].lower(), str(record[i]))
            else:
                setattr(p, fields[i][0].lower(), '')
        result.append(p)
    return result

def getfielddict():
    import copy
    fieldinfo = get_table_content('tblcasedict')
    basefieldinfo = fieldinfo[:]
    for prefix in ['ms_', 'sp_', 'ss_']:
        for field in basefieldinfo:
            newfield = copy.deepcopy(field)
            newfield.db_fieldname = prefix+field.db_fieldname
            newfield.show_fieldname = prefix.replace('_', ' ').upper() + field.show_fieldname
            fieldinfo.append(newfield)
    return fieldinfo

def get_qc_instance_id_list():
    users = get_data_from_sql('select qc_test_instance_id from tblallcase;')
    users.sort()
    return users
# def get_curr_fb():
#     sql = 'select name from tbldatesegment where curdate() between start_date and end_date;'
#     result = get_data_from_sql_m(sql)
#     if result:
#         return result[0][0]
#     else:
#         return ''



# print [x[0] for x in get_table_columns('tblscenario')]
# test()
# print get_scenario_check_fields()
# print get_user_list()

