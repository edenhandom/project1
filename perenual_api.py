import requests
import json
import sqlite3

API_KEY = 'sk-DFJP667c913a4a5396041'
BASE_URL_PLANT_LIST = f'https://perenual.com/api/species-list?key={API_KEY}&indoor=1'
BASE_URL_PLANT_DETAILS = f'https://perenual.com/api/species/details/{{ID}}?key={API_KEY}&indoor=1'

conn = sqlite3.connect('plants.db')
cursor = conn.cursor()


def create_tables():
    cursor.execute('DROP TABLE IF EXISTS plant_id')
    cursor.execute('DROP TABLE IF EXISTS plant_data')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plant_id (
        id INTEGER PRIMARY KEY
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plant_data (
        id INTEGER PRIMARY KEY,
        common_name TEXT,
        scientific_name TEXT,
        sunlight TEXT,
        watering TEXT,
        watering_period TEXT,
        maintenance TEXT,
        description TEXT,
        type TEXT
    )
    ''')
    conn.commit()


def store_plant_ids():
    response_plant_list = requests.get(BASE_URL_PLANT_LIST, params={'key': API_KEY})
    if response_plant_list.status_code == 200:
        data = response_plant_list.json()
        if 'data' in data:
            plants = data['data']
            for plant in plants:
                plant_id = plant.get('id')
                if plant_id:
                    cursor.execute('SELECT id FROM plant_id WHERE id = ?', (plant_id,))
                    existing_id = cursor.fetchone()
                    if not existing_id:
                        cursor.execute('''
                        INSERT INTO plant_id (id)
                        VALUES (?)
                        ''', (plant_id,))
    else:
        print("Failed to fetch")
    conn.commit()


def store_plant_data(plant_id, watering_pref, maintenance_pref):
    response_plant_details = requests.get(BASE_URL_PLANT_DETAILS.format(ID=plant_id))
    if response_plant_details.status_code == 200:
        data = response_plant_details.json()
        if data: #added
            id = data.get('id', 'Unknown')
            common_name = data.get('common_name', 'Unknown')
            scientific_name = data.get('scientific_name', [])
            sunlight = data.get('sunlight', [])
            watering = data.get('watering', 'Unknown').lower()
            watering_period = data.get('watering_period', 'Unknown')
            maintenance = data.get('maintenance', 'Unknown').lower()

            description = data.get('description', 'Unknown')
            type = data.get('type', 'Unknown')
            
            sunlight_str = ', '.join(sunlight)
            scientific_name = scientific_name[0] if scientific_name else 'Unknown'

            cursor.execute('''
            INSERT INTO plant_data (
                id, common_name, scientific_name, sunlight, watering, watering_period, maintenance, description, type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (plant_id, common_name, scientific_name, sunlight_str, watering, watering_period, maintenance, description, type)
            )
            conn.commit()
    else:
        print("Failed to fetch")


def match_plants(sunlight_pref, watering_pref, maintenance_pref):
    cursor.execute('''
    SELECT * FROM plant_data
    WHERE (sunlight LIKE ? OR ? = '')
    AND (watering LIKE ? OR ? = '')
    AND (maintenance LIKE ? OR ? = '')
    
    ''', (f'%{sunlight_pref}%', sunlight_pref, f'%{watering_pref}%', watering_pref, 
          f'%{maintenance_pref}%', maintenance_pref, 
          ))

    matches = cursor.fetchall()
    if matches:
        print("\nMatching Plants:")
        print()
        temp_matches = matches[:5]
        for match in temp_matches:
            print(f"Common Name: {match[1]}\n"
                  f"Scientific Name: {match[2]}\n"
                  f"Sunlight: {match[3]}\n"
                  f"Watering: {match[4]}\n"
                  f"Watering period: {match[5]}\n"
                  f"Maintenance: {match[6]}\n"
                  f"Type: {match[8]}\n\n"
                  f"Description: {match[7]}\n")
    else:
        print("No matches found :( Maybe a plastic plant is better for you...)")


def validate_input(prompt, valid_options):
    while True:
        user_input = input(prompt).lower()
        if user_input in valid_options:
            return user_input
        else:
            print(f"Invalid input. Please use the examples given and enter one of the following options: {', '.join(valid_options)}")


def main():
    create_tables()

    sunlight_options = ['full sun', 'part shade', 'full shade', 'part sun/part shade'] 
    watering_options = ['frequent', 'minimum', 'average']  
    maintenance_options = ['low', 'moderate', 'high'] 

    print("Please enter your plant preferences:")
    sunlight_pref = validate_input("Preferred sunlight (e.g., 'full sun', 'part shade', 'full shade', 'part sun/part shade'): ", sunlight_options)
    watering_pref = validate_input("Preferred watering (e.g., 'frequent', 'minimum', 'average'): ", watering_options)
    maintenance_pref = validate_input("Preferred maintenance level (e.g., 'low', 'moderate', 'high'): ", maintenance_options)

    store_plant_ids()

    cursor.execute('SELECT id FROM plant_id')
    ids_list = [row[0] for row in cursor.fetchall()]

    for id_from_list in ids_list:
        store_plant_data(id_from_list, watering_pref, maintenance_pref)

    match_plants(sunlight_pref, watering_pref, maintenance_pref)

main()
