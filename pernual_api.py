import requests
import json
import sqlite3

'''
Data we want from the API:
- name, scientific name, type (aka tree), watering, watering period, poisonous to pets/humans, indoor, sunlight 
'''

API_KEY = 'sk-X8KK667c51ee33cf36041'
BASE_URL_PLANT_LIST = f'https://perenual.com/api/species-list?key={API_KEY}'
BASE_URL_PLANT_DETAILS = f'https://perenual.com/api/species/details/{{ID}}?key={API_KEY}'

# Connect to SQLite databse
conn = sqlite3.connect('plants.db')
cursor = conn.cursor()

# Function to create tables
def create_tables():

    # Drop the tables if they exist (avoid duplicate errors)
    cursor.execute('DROP TABLE IF EXISTS plant_id')
    cursor.execute('DROP TABLE IF EXISTS plant_data')

    # Table for plant ids
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plant_id (
        id INTEGER PRIMARY KEY
    )
    ''')
    
    # Table for plant details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plant_data (
        id INTEGER PRIMARY KEY,
        common_name TEXT,
        scientific_name TEXT,
        sunlight TEXT,
        water TEXT,
        maintenance TEXT,
        poisonous_to_human BOOLEAN,
        poisonous_to_pets BOOLEAN,
        indoor BOOLEAN,
        type TEXT
    )
    ''')
    conn.commit()
# Done with creating tables

# Store plant IDs from plant API in plant id table
def store_plant_ids():
    response_plant_list = requests.get(BASE_URL_PLANT_LIST)
    if response_plant_list.status_code == 200:
        data = response_plant_list.json()
        if 'data' in data:
            plants = data['data']
            for plant in data:
                plant_id = plant.get('id')
                if plant_id:
                    cursor.execute('SELECT id FROM plant_id WHERE id = ?', (plant_id,))
                    existing_id = cursor.fetchone()
                if not existing_id:
                    cursor.execute('''
                    INSERT INTO plant_id (id)
                    VALUES (?)
                    ''', (plant_id,))
        conn.commit()
    else:
        print("Failed to fetch")

# Function to store plant details plant data table
def store_plant_data(plant_id):
    response_plant_details = requests.get(BASE_URL_PLANT_DETAILS.format(ID=plant_id))
    if response_plant_details.status_code == 200:
        
        data = response_plant_details.json()
        
        id = data.get('id', 'Unknown')
        common_name = data.get('common_name', 'Unknown')
        scientific_name = data.get('scientific_name', [])
        sunlight = data.get('sunlight', [])
        water = data.get('water', 'Unknown')
        maintenance = data.get('maintenance', 'Unknown')
        poisonous_to_human = data.get('poisonous_to_human', False)
        poisonous_to_pets = data.get('poisonous_to_pets', False)
        indoor = data.get('indoor', False)
        type = data.get('type', 'Unknown')
        sunlight_str = ', '.join(sunlight)
        scientific_name = scientific_name[0] if scientific_name else 'Unknown'

        cursor.execute('''
        INSERT INTO plant_data (
            id, common_name, scientific_name, sunlight, water, maintenance, 
            poisonous_to_human, poisonous_to_pets, indoor, type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (plant_id, common_name, scientific_name, sunlight_str, water, maintenance, 
              poisonous_to_human, poisonous_to_pets, indoor, type))
        conn.commit()
    else:
        print("Failed to fetch")


def main():
    create_tables()
    store_plant_ids()
    
    cursor.execute('SELECT id FROM plant_id')
    ids_list = [row[0] for row in cursor.fetchall()]

    for id_from_list in ids_list:
        store_plant_data(id_from_list)
    
    cursor.execute('SELECT * FROM plant_data')
    print(cursor.fetchall())

main()
    








    
    
    
    
    
    
""" 
! scrapped perhaps ! 
make plant ids list
    response_plant_list = requests.get(BASE_URL_PLANT_LIST)
    data_plant_list = response_plant_list.json()
    # maybe need this?
    df_plant_list = pd.DataFrame(data_plant_list)

    ids = df_plant_list['data'][0].tolist()

    data_plant_details_list = []
    
    df_plant_list.to_sql('plant_id', conn, if_exists = 'replace', index=False)
    df_plant_details.to_sql('plant_data', conn, if_exists = 'replace', index=False)

    query = '''
    SELECT *
    FROM plant_id
    INNER JOIN plant_data ON plant_id.id = plant_data.id;

    '''

    result = pd.read_sql_query(query, conn)

    conn.commit()
    print(result)
"""

        


