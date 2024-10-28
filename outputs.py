import csv
import os

def save_results_to_csv(self):
    results = {eng.name: eng.score for eng in self.engineers}
    
    filename = 'results.csv'
    
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name'] + ['Game 1'])
            for name, score in results.items():
                writer.writerow([name, score])
    else:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            game_number = len(headers) - 1
            new_game_column = f'Game {game_number + 1}'

        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for row in rows:
            name = row['Name']
            if name in results:
                row[new_game_column] = results[name]

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers + [new_game_column])
            writer.writeheader()
            writer.writerows(rows)

    # Read and store the CSV data
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    # Store the CSV data in the game state
    self.csv_results = csv_data

    return csv_data  # Return the CSV data if needed elsewhere
