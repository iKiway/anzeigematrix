from db_api.Station import Station
import datetime


station = Station("Rommelshausen","529fc99d86062cff082818f1820c4900","ef252166427b5094f093b9e5f331508c")
station.get_sorted_departure_list()