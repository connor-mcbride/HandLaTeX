import psycopg2
import csv
import json


def create_csv(csv_file='strokes.csv'):
    """Extract the stroke data from a sql database to create a csv with the data."""
    # Load database configuration from a separate file
    with open('db_config.json') as config_file:
        config = json.load(config_file)

    conn = psycopg2.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"]
    )

    cursor = conn.cursor()

    # id, key, strokes
    sql_query = 'SELECT id, key, strokes FROM samples'
    cursor.execute(sql_query)

    results = cursor.fetchall()

    # Write into new csv file
    with open(csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['id', 'key', 'strokes'])  # Write the header
        csvwriter.writerows(results)  # Write the data rows

    # Commit and close connection
    conn.commit()
    cursor.close()
    conn.close()


def normalize_data(input_file='strokes.csv', output_file='normalized_strokes.csv'):
    """Reads in existing stroke data csv and normalizes it to perform better during training."""
    with open(input_file, 'r') as file:
        csvreader = csv.reader(file)
        rows = list(csvreader)

    cleaned_rows = []

    for i, row in enumerate(rows):
        if i == 0:
            # Include header row
            cleaned_rows.append(row[:2] + ['flattened_points'])
            continue

        # Parse the JSON data in the third column
        strokes_data = json.loads(row[2].replace("'", '"'))

        # Flatten the strokes into a single list of points
        points = [point for stroke in strokes_data for point in stroke]

        # Get first point coordinates
        x_0, y_0, t_0 = points[0]

        # Initialize max_x and max_y
        max_x = 0
        max_y = 0

        # Adjust points and find max_x and max_y in one pass
        for point in points:
            # Adjust points
            point[0] -= x_0
            point[1] -= y_0
            point[2] -= t_0

            # Track maximum absolute values
            abs_x = abs(point[0])
            abs_y = abs(point[1])

            if abs_x > max_x:
                max_x = abs_x
            if abs_y > max_y:
                max_y = abs_y

        # Avoid division by zero
        max_x = max_x or 1
        max_y = max_y or 1

        # Normalize points
        for point in points:
            point[0] /= max_x
            point[1] /= max_y

        # Update row with flattened points
        row[2] = json.dumps(points)

        cleaned_rows.append(row)

    # Write the normalized data
    with open(output_file, 'w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerows(cleaned_rows)


def create_symbol_map(input_file='symbols.json', output_file='latex_conversion.json'):
    """Create a JSON file mapping unique keys to their corresponding strokes."""
    with open(input_file, 'r') as file:
        data = json.load(file)

    symbol_map = {}

    for symbol in data:
        command = symbol['command']
        mathmode = symbol['mathmode']
        textmode = symbol['textmode']
        symbol_id = symbol['id']
        css_class = symbol['css_class']

        symbol_data = {
            'command': command,
            'mathmode': mathmode,
            'textmode': textmode,
            'css_class': css_class
        }

        if 'package' in symbol:
            symbol_data |= {
                'package': symbol['package']
            }

        if 'fontenc' in symbol:
            symbol_data |= {
                'fontenc': symbol['fontenc']
            }

        symbol_map[symbol_id] = symbol_data

    with open(output_file, 'w') as json_file:
        json.dump(symbol_map, json_file, indent=4)