#!/usr/bin/env python3

import os
import sys
import urllib.request

URL = os.environ.get('PAINTSHOP_URL', "0.0.0.0:8080/v1")


def no_space_list(input_list):
    return '[' + ','.join(map(str, input_list)) + ']'


def process_content(content):
    output = []
    testcases = int(content[0])
    content = content[1:]
    for c in range(testcases):
        number_of_colors = int(content[0])
        number_of_customers = int(content[1])
        customer_demand = []
        for l in range(number_of_customers):
            demand = list(map(int, content[l + 2].split()))
            customer_demand.append(demand)
        no_space_demands = '[' + ','.join(map(no_space_list, customer_demand)) + ']'
        solution = urllib.request.urlopen(
            "http://{}/?input={{\"colors\":{},\"customers\":{},\"demands\":{}}}".format(URL, number_of_colors,
                                                                                        number_of_customers,
                                                                                        no_space_demands)).read()
        output.append("Case #{}: {}".format(c + 1, solution.decode('utf-8')))
        content = content[number_of_customers + 2:]
    return output


def main(input_file):
    with open(input_file) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    for line in process_content(content):
        print(line)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    elif 'input.txt' in os.listdir('.'):
        main('input.txt')
    else:
        print("Where is my input? input.txt does not exist, Create one, or provide a filename as an argument")
