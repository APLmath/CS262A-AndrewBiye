# Uniformly sample the data in 100 chunks.

import csv
import random

f = open('all.csv')
reader = csv.DictReader(f)
field_names = reader.fieldnames
data = list(reader)
f.close()

random.shuffle(data)

#data = data[0:len(data) / 10]

f = open('earthquakes.csv', 'w')
writer = csv.DictWriter(f, field_names)
writer.writeheader()
writer.writerows(data)
f.close()

num_chunks = 100
for i in range(num_chunks):
  chunk = data[i * len(data) / num_chunks:(i + 1) * len(data) / num_chunks]
  f = open('earthquakes_' + str(i) + '.csv', 'w')
  writer = csv.DictWriter(f, field_names)
  writer.writeheader()
  writer.writerows(chunk)
  f.close()
