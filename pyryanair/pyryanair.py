import json
import os
import requests
import xlsxwriter


class PyRyanAir:
    def __init__(self):
        self.airports = json.loads(open('airports.json', 'r').read())
        self.current_location = None
        self.destination = None
        self.cities = {}
        self.arrival_cities = {}
        self.getCities()
        self.menu = {}
        self.paramIn = []
        self.search(show=False)
        self.flights = []
        self.export_flights = {
            'origin': [],
            'originName': [],
            'destination': [],
            'destinationName': [],
            "timeUTC_start": [],
            "timeUTC_end": [],
            "faresLeft": [],
            "flightKey": [],
            "infantsLeft": [],
            "operatedBy": [],
            "flightNumber": [],
            "duration": [],
            "type": [],
            "amount": [],
            "count": [],
            "hasDiscount": [],
            "publishedFare": [],
            "discountInPercent": [],
            "hasPromoDiscount": [],
            "discountAmount": [],
            "hasBogof": []
        }
        self.standard_data = []

    def getCities(self, airports=None, arrival_cities=False):
        if airports is None:
            airports = self.airports
        if arrival_cities:
            cities = self.arrival_cities
        else:
            self.cities = {}
            cities = self.cities
        for locations in range(len(airports)):
            city_name = airports[locations]['city']['name']
            if city_name not in cities.keys():
                cities[city_name] = [locations]
            else:
                cities[city_name].append(locations)

    def search(self, keyword=None, show=True, cities_var=None):
        self.menu = {}
        i = 0
        if cities_var is None:
            if self.current_location is not None:
                cities = self.arrival_cities
            else:
                cities = self.cities
        else:
            cities = cities_var
        for city in cities:
            if keyword:
                if keyword.lower() in city.lower():
                    print(f'{i}. {city}')
                    self.menu[i] = city
                    i += 1
            else:
                if show:
                    print(f'{i}. {city}')
                self.menu[i] = city
                i += 1

    def filledParameters(self):
        if self.current_location and self.destination:
            return 1
        else:
            return -1

    def userInputs(self):
        user_input = '0'
        print('HELP MENU\n\n'
              ' all           -> To print all the cities/airports available\n'
              ' s-Keyword     -> To search for a city code\n'
              ' c-IDOfTheCity -> To Choose Current Location\n'
              ' d-IDOfTheCity -> To Choose Destination\n'
              ' clear         -> Clear terminal\n')
        while user_input != '-1':
            user_input = input('#- ')
            if user_input.lower() == 'all':
                self.search()
            elif user_input == 'clear':
                os.system('cls||clear')
            elif 's-' in user_input:
                self.search(user_input.split('s-')[1])
            elif 'c-' in user_input:
                self.current_location = self.menu[int(user_input.split('c-')[1])]
                print(f'CURRENT LOCATION => {self.current_location}')

                for origins in self.cities[self.current_location]:
                    self.getCities(self.getRoutes(self.airports[origins]['code']), arrival_cities=True)
                self.search(show=False)
                if self.filledParameters() == 1: break
            elif 'd-' in user_input:
                self.destination = self.menu[int(user_input.split('d-')[1])]
                print(f'DESTINATION => {self.destination}')
                if self.filledParameters() == 1: break

        # paramIn = ['Out Date (eg. 2023-12-31): ', 'Flexible Day Before (eg. 2): ', 'Flexible Days After (eg. 2): ']
        paramIn = ['Out Date (eg. 2023-12-31): ']
        for param in paramIn:
            self.paramIn.append(input(param))

        self.combineFlights()

    def getRoutes(self, destination):
        url = f"https://www.ryanair.com/api/locate/v5/routes?departureAirportCode={destination}&fields=connectingAirport.code&fields=connectingAirport.name&fields=connectingAirport.seoName&fields=connectingAirport.base&fields=connectingAirport.timeZone&fields=connectingAirport.aliases&fields=connectingAirport.city.code&fields=connectingAirport.city.name&fields=connectingAirport.coordinates.latitude&fields=connectingAirport.coordinates.longitude&fields=connectingAirport.macCity.code&fields=connectingAirport.macCity.name&fields=connectingAirport.macCity.macCode&fields=connectingAirport.region.code&fields=connectingAirport.region.name&fields=connectingAirport.country.code&fields=connectingAirport.country.name&fields=connectingAirport.country.currency&fields=connectingAirport.base&fields=arrivalAirport.code&fields=arrivalAirport.name&fields=arrivalAirport.seoName&fields=arrivalAirport.base&fields=arrivalAirport.timeZone&fields=arrivalAirport.aliases&fields=arrivalAirport.city.code&fields=arrivalAirport.city.name&fields=arrivalAirport.coordinates.latitude&fields=arrivalAirport.coordinates.longitude&fields=arrivalAirport.macCity.code&fields=arrivalAirport.macCity.name&fields=arrivalAirport.macCity.macCode&fields=arrivalAirport.region.code&fields=arrivalAirport.region.name&fields=arrivalAirport.country.code&fields=arrivalAirport.country.name&fields=arrivalAirport.country.currency&fields=arrivalAirport.base&fields=operator&market=en&distinct=true"

        payload = {}
        headers = {
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'tracestate': '646832@nr=0-1-646832-389251397-8e35f83ad98756ad----1658261968496',
            'traceparent': '00-c6647c0293e0f8e57a9b82e830c0f130-8e35f83ad98756ad-01',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjY0NjgzMiIsImFwIjoiMzg5MjUxMzk3IiwiaWQiOiI4ZTM1ZjgzYWQ5ODc1NmFkIiwidHIiOiJjNjY0N2MwMjkzZTBmOGU1N2E5YjgyZTgzMGMwZjEzMCIsInRpIjoxNjU4MjYxOTY4NDk2fX0=',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        ans = []
        if response.status_code == 200:
            for i in response.json():
                ans.append(i['arrivalAirport'])
            return ans

    def getFlightsFromRyanAir(self, destination: str, origin: str):
        # print(destination, origin)
        url = f"https://www.ryanair.com/api/booking/v4/en-us/availability?ADT=1&CHD=0&DateIn=&DateOut={self.paramIn[0]}&Destination={destination}&Disc=0&INF=0&Origin={origin}&TEEN=0&promoCode=&IncludeConnectingFlights=false&FlexDaysBeforeOut=2&FlexDaysOut=2&ToUs=AGREED&RoundTrip=false&ChangeFlight=undefined"
        # print(url)
        headers = {
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = requests.request("GET", url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            return response.json()['trips']

    def combineFlights(self):
        for origins in self.cities[self.current_location]:
            for destination in self.cities[self.destination]:
                flight_req = self.getFlightsFromRyanAir(self.airports[destination]['code'],
                                                        self.airports[origins]['code'])
                if flight_req != -1:
                    self.flights.append(flight_req)

        self.exportData()

    def dictAddVal(self, bigDict, varDict):
        for dict_ in bigDict:
            for key in dict_.keys():
                # print(key)
                if key not in varDict.keys():
                    varDict[key] = []
                varDict[key].append(dict_[key])

    def addFare(self):
        keys = ['type', 'amount', 'count', 'hasDiscount', 'publishedFare', 'discountInPercent', 'hasPromoDiscount',
                'discountAmount', 'hasBogof']
        for key in keys:
            self.export_flights[key].append('')

    def addFlight(self, flights):
        for flight in flights:
            try:
                # flight = flight[0]
                self.dictAddVal(flight['regularFare']['fares'], self.export_flights)

                simple_keys = ['faresLeft', 'flightKey', 'infantsLeft', 'operatedBy', 'flightNumber', 'duration']
                for key in simple_keys:
                    if key not in self.export_flights.keys():
                        self.export_flights[key] = []
                    self.export_flights[key].append(flight[key])
                # print(self.export_flights)
                # print(flight['timeUTC'], flight['time'])
                self.export_flights['timeUTC_start'].append(flight['timeUTC'][0].replace('T', ' ').split('Z')[0])
                self.export_flights['timeUTC_end'].append(flight['timeUTC'][1].replace('T', ' ').split('Z')[0])

            except:
                return -1

    def exportData(self):
        for flights in self.flights:
            for flight in flights:
                if flight is not None:
                    for dates in flight['dates']:
                        if len(dates['flights']) > 0:
                            if self.addFlight(dates['flights']) == -1:
                                keys_ = ['origin', 'originName', 'destination', 'destinationName']
                                for key in keys_:
                                    self.export_flights[key].append(flights[0][key])
                                print(dates['flights'])

        self.writeData()

    def writeData(self):
        workbook = xlsxwriter.Workbook(
            f'flights_{self.current_location}_{self.destination}.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:Z', 15)
        worksheet.set_row(0, 12)
        col_num = 0
        for key, value in self.export_flights.items():
            worksheet.write(0, col_num, key)
            worksheet.write_column(1, col_num, value)
            col_num += 1

        workbook.close()
