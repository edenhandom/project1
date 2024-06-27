import requests
import json
import sqlite3

'''
Data we want from the API:
- name, scientific name, type (aka tree), watering, watering period,
poisonous to pets/humans, indoor, sunlight
'''

API_KEY = 'sk-DFJP667c913a4a5396041'
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
        watering TEXT,
        watering_period TEXT,
        maintenance TEXT,

        type TEXT
    )
    ''')
    conn.commit()
# Done with creating tables


# Store plant IDs from plant API in plant id table
def store_plant_ids():
    # Picked a random window of data from the API to look at
    page = 160
    while page <= 162:
        response_plant_list = requests.get(BASE_URL_PLANT_LIST, params={'key': API_KEY, 'page': page})
        # If request is successful
        if response_plant_list.status_code == 200:
            # Grab JSON data from the API
            data = response_plant_list.json()
            if 'data' in data:
                # Grab dictionary of plant items in API data
                plants = data['data']
                if not plants:
                    break
                # Look at each plant item in dictionary, grab plant ID value
                for plant in plants:
                    plant_id = plant.get('id')
                    # If the plant item is not of type "tree", add to ID table
                    if plant_id and (plant.get("type") != 'tree'):
                        cursor.execute('SELECT id FROM plant_id WHERE id = ?', (plant_id,))
                        existing_id = cursor.fetchone()
                        if not existing_id:
                            cursor.execute('''
                            INSERT INTO plant_id (id)
                            VALUES (?)
                            ''', (plant_id,))
                page += 1
            else:
                break
        else:
            print("Failed to fetch")
            break
    conn.commit()


# Function to store plant details in plant data table
def store_plant_data(plant_id):
    response_plant_details = requests.get(BASE_URL_PLANT_DETAILS.format(ID=plant_id))
    # Check if request is successful
    if response_plant_details.status_code == 200:
        # Store response
        data = response_plant_details.json()

        # Grab plant details
        id = data.get('id', 'Unknown')
        common_name = data.get('common_name', 'Unknown')
        scientific_name = data.get('scientific_name', [])
        sunlight = data.get('sunlight', [])
        watering = data.get('watering', 'Unknown')
        watering_period = data.get('watering_period', 'Unknown')
        maintenance = data.get('maintenance', 'Unknown')
        type = data.get('type', 'Unknown')

        # Formatting
        sunlight_str = ', '.join(sunlight)
        scientific_name = scientific_name[0] if scientific_name else 'Unknown'

        # Store in plant details table
        cursor.execute('''
        INSERT INTO plant_data (
            id, common_name, scientific_name, sunlight, watering, watering_period, maintenance, type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (plant_id, common_name, scientific_name, sunlight_str, watering, watering_period, maintenance, type)
        )
        conn.commit()
    else:
        print("Failed to fetch")


# Function to match user to plant based on preferences
def match_plants():
    print("Please enter your plant preferences:")
    sunlight_pref = input("Preferred sunlight (e.g., 'full sun', 'partial shade'): ").lower()
    watering_pref = input("Preferred watering (e.g., 'moderate', 'low'): ").lower()
    watering_time_pref = input("Preferred watering window (eg. 'morning'): ").lower()

    cursor.execute('''
    SELECT * FROM plant_data
    WHERE sunlight LIKE ? OR watering LIKE ? or watering_period LIKE ?
    ''', (f'%{sunlight_pref}%', f'%{watering_pref}%', f'%{watering_time_pref}'))

    matches = cursor.fetchall()
    if matches:
        print("\nMatching Plants:")
        for match in matches:
            print(f"Common Name: {match[1]}, Scientific Name: {match[2]}, Sunlight: {match[3]}, "
                  f"Watering: {match[4]}, Watering period: {match[5]}, Maintenance: {match[6]}")
    else:
        print("No matches found.")


def main():
    create_tables()
    store_plant_ids()

    cursor.execute('SELECT id FROM plant_id')
    ids_list = [row[0] for row in cursor.fetchall()]

    for id_from_list in ids_list:
        store_plant_data(id_from_list)

    match_plants()

    # cursor.execute('SELECT * FROM plant_data')
    # print(cursor.fetchall())


main()

'''
Prompt input from user
- Create table to hold user input (if need be, group by in sql)
Create matching alogorithm
- Take user input and select plant from plant_data that closely matches input : abi
- Match user to plant based on input : eden
- unit test : eden
- style guide: abi
- read me  : abi
- pitch deck : eden


Unittest
Pep 8
'''
