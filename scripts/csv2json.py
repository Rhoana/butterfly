import sys
import csv
import json

if __name__ == "__main__":

    IN = "in.txt"
    OUT = "out.json"
    
    if len(sys.argv) > 1:
        IN = sys.argv[1]

    if len(sys.argv) > 2:
        OUT = sys.argv[2]

    # Make empty output
    soma_out = []

    # Read from CSV file
    with open(IN, 'r') as cf:
        for soma in csv.reader(cf):

            # Make an dict from csv
            k_soma = ['neuron_id', 'z', 'y', 'x']
            soma_dict = dict(zip(k_soma, soma))
            # Add to output
            soma_out.append(soma_dict)

    # Write to JSON file
    with open(OUT, 'w') as jf:
        json.dump(soma_out, jf)
