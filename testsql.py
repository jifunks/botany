import sqlite3

garden_db_path = "sqlite/garden_db.sqlite"

def init_database():
    #TODO: does this need permissions?
    conn = sqlite3.connect(garden_db_path)
    init_table_string = """CREATE TABLE IF NOT EXISTS garden (
    plant_id tinytext PRIMARY KEY,
    owner text,
    description text,
    age text,
    score integer,
    is_dead text
    )"""

    c = conn.cursor()
    c.execute(init_table_string)
    conn.close()
def update_garden_db():
    # insert or update this plant id's entry in DB (should happen
    # regularly)
    # TODO: create a second function that is called to retrieve garden
    # when called by display controller


    conn = sqlite3.connect(garden_db_path)
    c = conn.cursor()
    ##try to insert or replace
    update_query = """INSERT OR REPLACE INTO garden (
                plant_id, owner, description, age, score, is_dead
                ) VALUES (
                '{pid}', '{pown}', '{pdes}', '{page}', {psco}, '{pdead}'
                )
                """.format(pid = "asdfaseeeedf", pown = "jaeeke", pdes = "bigger ceeooler plant", page="28dee", psco = str(244400), pdead = str(False))
    # update_query = """INSERT INTO garden (
    #             plant_id, owner, description, age, score, is_dead
    #             ) VALUES (
    #             '{pid}', '{pown}', '{pdes}', '{page}', {psco}, '{pdead}'
    #             )
    #             """.format(pid = "asdfasdf", pown = "jake", pdes = "big cool plant", page="25d", psco = str(25), pdead = str(False))

    print(c.execute(update_query))
    conn.commit()
    conn.close()
    #print("bigggg booom")

def retrieve_garden_from_db(garden_db_path):
    # Builds a dict of dicts from garden sqlite db
    garden_dict = {}
    conn = sqlite3.connect(garden_db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM garden ORDER BY owner')
    tuple_list = c.fetchall()
    conn.close()
    # Building dict from table rows
    for item in tuple_list:
        garden_dict[item[0]] = {
            "owner":item[1],
            "description":item[2],
            "age":item[3],
            "score":item[4],
            "dead":item[5],
        }
    return garden_dict

#init_database()
#update_garden_db()
results = retrieve_garden_from_db(garden_db_path)
print(results)


# con = sqlite3.connect(garden_db_path) #
# con.row_factory = sqlite3.Row #
# cur = con.cursor() #
# cur.execute("select * from garden ORDER BY score desc") #
# blah = cur.fetchall() #
# con.close()
# print(blah)



