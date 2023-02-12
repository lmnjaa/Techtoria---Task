# CLI command
import requests
import csv
import sys

# get the command line arguments
place, start_date, end_date = sys.argv[1], sys.argv[2], sys.argv[3]

# construct the URL for the data request
base_url = 'https://open-meteo.com/en/docs'
params = {'place': place, 'start_date': start_date, 'end_date': end_date}
url = base_url + '?' + '&'.join([k+'='+v for k,v in params.items()])

response = requests.get(url)
data = response.json()

# write the data to a CSV file
with open('weather_data.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Place Name', 'Date', 'Min Temperature', 'Max Temperature', 'Max Wind Speed', 'Precipitation Sum', 'Measured/Forecast'])
    for row in data:
        writer.writerow([row['place'], row['date'], row['min_temperature'], row['max_temperature'], row['max_wind_speed'], row['precipitation_sum'], row['measured_forecast']])

# print the CSV file
print('Weather data written to weather_data.csv')

# REST web service
import csv
import json
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# read the CSV file and store into a SQLite database
conn = sqlite3.connect('weather_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS weather_data (
    place text,
    date text,
    min_temperature real,
    max_temperature real,
    max_wind_speed real,
    precipitation_sum real,
    measured_forecast text
)''')

with open('weather_data.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    for row in reader:
        c.execute("INSERT INTO weather_data VALUES (?,?,?,?,?,?,?)", row)

conn.commit()

# query the database for the requested place
@app.route('/differences', methods=['GET'])
def get_differences():
    place = request.args.get('place')
    c.execute("SELECT * FROM weather_data WHERE place=?", (place,))
    data = c.fetchall()
    differences = []
    for row in data:
        if row[-1] == 'measured':
            measured = row[2:6]
            c.execute("SELECT * FROM weather_data WHERE place=? AND measured_forecast='forecast' AND date=?", (place, row[1]))
            forecast = c.fetchone()[2:6]
            differences.append({
                'date': row[1],
                'differences': [measured[i] - forecast[i] for i in range(len(measured))]
            })
    return json.dumps(differences)

if __name__ == '__main__':
    app.run()



# Tests

# Test 1:
def test_command_line_args():
    # test that command line arguments are correctly assigned
    sys.argv = ["place", "start_date", "end_date"]
    place, start_date, end_date = sys.argv[1], sys.argv[2], sys.argv[3]
    assert place == "place"
    assert start_date == "start_date"
    assert end_date == "end_date"

# Test 2:
def test_url_construction():
    # test that the URL is correctly constructed
    base_url = 'https://open-meteo.com/en/docs'
    params = {'place': 'place', 'start_date': 'start_date', 'end_date': 'end_date'}
    url = base_url + '?' + '&'.join([k+'='+v for k,v in params.items()])
    assert url == "https://open-meteo.com/en/docs?place=place&start_date=start_date&end_date=end_date"

# Test 3:
def test_csv_file():
    # test that the CSV file is correctly written
    with open('weather_data.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)
        assert header == ['Place Name', 'Date', 'Min Temperature', 'Max Temperature', 'Max Wind Speed', 'Precipitation Sum', 'Measured/Forecast']

# Test 4:
def test_differences_endpoint():
    # test that the differences endpoint returns the correct data
    place = "place"
    c.execute("SELECT * FROM weather_data WHERE place=?", (place,))
    data = c.fetchall()
    differences = []
    for row in data:
        if row[-1] == 'measured':
            measured = row[2:6]
            c.execute("SELECT * FROM weather_data WHERE place=? AND measured_forecast='forecast' AND date=?", (place, row[1]))
            forecast = c.fetchone()[2:6]
            differences.append({
                'date': row[1],
                'differences': [measured[i] - forecast[i] for i in range(len(measured))]
            })
    assert differences == [{'date': row[1], 'differences': [measured[i] - forecast[i] for i in range(len(measured))]}]