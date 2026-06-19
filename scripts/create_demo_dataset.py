"""Create a small demo CSV dataset for quick local testing."""
import csv
import random
from datetime import datetime, timedelta


def create(path, rows=200):
    start = datetime.utcnow()
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['timestamp','intersection','vehicleCount','averageSpeed','pollutionIndex','signalPhase'])
        for i in range(rows):
            ts = (start + timedelta(minutes=i)).isoformat()
            w.writerow([ts, 'intersection-1', random.randint(0,50), round(random.uniform(20,60),1), random.randint(10,100), random.choice(['green','yellow','red'])])
    print('Wrote demo dataset to', path)


if __name__ == '__main__':
    create('data_import/datasets/demo_traffic.csv', rows=300)
