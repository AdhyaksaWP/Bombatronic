import geocoder
from geopy.geocoders import Nominatim

class Location():

    def __init__(self):
        self.__ip = None
        self.__latitude = None
        self.__longitude = None
        self.__current_location = None

    def __get_current_coords(self):
        self.__ip = geocoder.ip('me')
        if self.__ip.latlng is not None:
            return self.__ip.latlng
        else:
            return None
    
    def get_location(self):
        coords = self.__get_current_coords()
        if coords is not None:
            self.__latitude, self.__longitude = coords
            geoLoc = Nominatim(user_agent="GetLoc")
            self.__current_location = geoLoc.reverse(f"{self.__latitude}, {self.__longitude}")

            return self.__current_location
        else:
            return "Location not found!"