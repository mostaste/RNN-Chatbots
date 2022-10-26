import sqlite3
import json
from datetime import datetime

##################################################################################################################################################################################################################

""" Code Commences  """

year = "2008"
timeframe = ['2008-01', '2008-02', '2008-03']
sql_transaction = []
start_row = 0
cleanup = 1000000

connection = sqlite3.connect('{}.db'.format(year))
c = connection.cursor()


# Creates the table of the Database.
def create_table():
    c.execute("""CREATE TABLE IF NOT EXISTS parent_reply
              (parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE,
              parent TEXT, comment TEXT, subreddit TEXT,
              unix INT, score INT)""")


# Formats the data to turn it into a local string object
def format_data(data):
    data = data.replace('\n', ' newlinechar ').replace('\r', ' newlinechar ').replace('"', "'")
    return data


# Build up insertion statements in groups
def transaction_bldr(sql):
    global sql_transaction
    sql_transaction.append(sql)
    if len(sql_transaction) > 1000:
        c.execute('BEGIN TRANSACTION')
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        sql_transaction = []


# Replace the existing comment with the comment of the higher score
def sql_insert_replace_comment(commentid, parentid, parent, comment, subreddit, time, score):
    try:
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(
            parentid, commentid, parent, comment, subreddit, int(time), score, parentid)
        transaction_bldr(sql)

    except Exception as e:
        print('s0 insertion', str(e))


# Pair Comments with Parents
def sql_insert_has_parent(commentid, parentid, parent, comment, subreddit, time, score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(
            parentid, commentid, parent, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion', str(e))


# Insert Comments with no Parents
def sql_insert_no_parent(commentid, parentid, comment, subreddit, time, score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(
            parentid, commentid, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion', str(e))


# Finding and matching parent IDs with comments
def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        # print(str(e))
        return False


# Function to take in Useful Data
def acceptable(data):
    if len(data.split(' ')) > 50 or len(data) < 1:
        return False
    elif len(data) > 1000:
        return False
    elif data == '[deleted]':
        return False
    elif data == '[removed]':
        return False
    else:
        return True


# Find the score of the existing_comment_score
def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else:
            return False
    except Exception as e:
        # print(str(e))
        return False


def createDatabase(timeframe):
    print('\nCreating a Database... ...  ' + str(timeframe))
    create_table()
    row_counter = 0
    paired_rows = 0
    no_pair = 0;

    # //home//mostaste//Desktop//Deep Learning Projects//reddit_data//2015//RC_{}
    # TO-DO Create a counter to account for comments with no pairs
    with open(r'/home/mostaste/Desktop/Deep Learning Projects/Reddit Raw Data/2008/RC_{}'.format(timeframe), buffering=1000) as f:
        for row in f:
            # print(row)
            # time.sleep(555)
            row_counter += 1

            if row_counter > start_row:
                try:
                    row = json.loads(row)
                    parent_id = row['parent_id'].split('_')[1]
                    comment_id = row['id']
                    body = format_data(row['body'])
                    created_utc = row['created_utc']
                    score = row['score']



                    subreddit = row['subreddit']
                    parent_data = find_parent(parent_id)

                    existing_comment_score = find_existing_score(parent_id)
                    if existing_comment_score:
                        if score > existing_comment_score:
                            if acceptable(body):
                                sql_insert_replace_comment(comment_id, parent_id, parent_data, body, subreddit,
                                                           created_utc, score)

                    else:
                        if acceptable(body):
                            if parent_data:
                                if score >= 2:
                                    sql_insert_has_parent(comment_id, parent_id, parent_data, body, subreddit,
                                                          created_utc, score)
                                    paired_rows += 1
                            else:
                                sql_insert_no_parent(comment_id, parent_id, body, subreddit, created_utc, score)
                                no_pair += 1
                except Exception as e:
                    print(str(e))

            if row_counter % 100000 == 0:
                print('Total Rows Read: {}, Paired Rows: {}, Unpaired Rows: {}, Time: {}'.format(row_counter, paired_rows, no_pair, str(datetime.now())))

            if row_counter > start_row:
                if row_counter % cleanup == 0:
                    print("Cleanin up!")
                    sql = "DELETE FROM parent_reply WHERE parent IS NULL"
                    c.execute(sql)
                    connection.commit()
                    c.execute("VACUUM")
                    connection.commit()

        print("Database has been created!!")


##############################   Main Code   ##############################


if __name__ == '__main__':


    # for i in range(3):
    createDatabase(timeframe[1])
    createDatabase(timeframe[2])





##################################################################################################################################################################################################################