#!/usr/bin/env python3
import os
import sys
import unittest
import urllib

sys.path.append(os.path.join(os.path.dirname(__file__), '../application'))

from app import app

input_file = "testcases/unit-tests.in.txt"


def no_space_list(input_list):
    return '[' + ','.join(map(str, input_list)) + ']'


class V2TestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['LOGIN_DISABLED'] = True
        app.login_manager.init_app(app)
        self.app = app.test_client()

    def process_content(self, content):
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

            payload = dict(colors=number_of_colors, customers=number_of_customers, demands=no_space_demands)

            f = urllib.parse.urlencode(payload)
            f = f.encode('utf-8')

            response = self.app.post("/v2/", data=payload, follow_redirects=False)

            output.append("Case #{}: {}".format(c + 1, response.data))
            content = content[number_of_customers + 2:]
        return output

    def test_without_login(self):
        with open(input_file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        for line in self.process_content(content):
            print(line)


if __name__ == '__main__':
    unittest.main()
