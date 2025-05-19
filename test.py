from db_api.Station import Station
import datetime


station = Station("Rommelshausen","529fc99d86062cff082818f1820c4900","ef252166427b5094f093b9e5f331508c")
a = station.get_sorted_departure_list()

b = station.get_sorted_departure_list()
b = a

if a == b:
    print("equal")
else:
    print("not equal")
