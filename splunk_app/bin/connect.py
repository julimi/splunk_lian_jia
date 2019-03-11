import psycopg2
import splunk.Intersplunk
# import logging
# import logging.handlers
 
# def setup_logger(level):
#     logger = logging.getLogger('getlianjia')
#     logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
#     logger.setLevel(level)
 
#     file_handler = logging.handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/getlianjia.log', maxBytes=25000000, backupCount=5)
#     formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#     file_handler.setFormatter(formatter)
    
#     logger.addHandler(file_handler)
    
#     return logger

# # Setup the handler
# logger = setup_logger(logging.ERROR)

results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()

def helper(cid, rows):
    for row in rows:
        if row[0] == cid:
            return row[1]
    return "none"

def query_from_db(results):
    conn = None
    # splunk.Intersplunk.outputResults(results)
    try:
        conn = psycopg2.connect(host="127.0.0.1", database="lian-jia", user="wjiang")
        cur = conn.cursor()
        # print('PostgreSQL lian-jia content: \n')
        cur.execute('SELECT * FROM cities')
        rows1 = cur.fetchall()
        cur.execute('SELECT * FROM communities')
        rows2 = cur.fetchall()
        cur.close()
        for row in rows2:
            result = {}
            result['id'] = row[2]
            result['city_id'] = helper(row[1], rows1)
            result['district_id'] = row[2]
            result['biz_circle_id'] = row[3]
            result['name'] = row[4]
            result['building_finish_year'] = row[5]
            result['building_type'] = row[6]
            result['second_hand_quantity'] = row[7]
            result['second_hand_unit_price'] = row[8]
            row9 = ""
            if row[9]:
                for k, v in row[9].items():
                    if v:
                        row9 += k + ': ' + v + '\n\n'
                    else:
                        row9 += k + ': none ' + '\n\n'
            result['detail'] = row9
            results.append(result)
        # print(length)
    except (Exception, psycopg2.DatabaseError) as error:
        splunk.Intersplunk.generateErrorResults(error)
    finally:
        if conn is not None:
            conn.close()
            splunk.Intersplunk.outputResults(results)

query_from_db(results)
