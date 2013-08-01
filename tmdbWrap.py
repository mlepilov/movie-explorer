import datetime
import urllib
import urllib2
import json

# This is the unique API key for TMDb given to each developer; this particular
# one belongs to Mikhail Lepilov.
api_key = 'a1c96b8cef6c9961330b81bd8a508376'

class tmdbWrap:

    movielist = []

    def __init__(self, query):
        self.__sargs = {'api_key':api_key, 'query':query, 'include_adult':False}
        self.__url = 'http://api.themoviedb.org/3/search/movie?%s' % urllib.urlencode(self.__sargs)
        self.__req = urllib2.Request(self.__url)
        self.__req.add_header('Accept', 'application/json')
        self.__req.lifetime = 3600
        self.__page = urllib2.urlopen(self.__req)
        self.__data = json.load(self.__page)
        for item in self.__data['results']:
            self.movielist.append(Movie(item['id']))


class Movie:
    def __init__(self, id):
        self.__sargs = {'api_key':api_key}
        self.__url = 'http://api.themoviedb.org/3/movie/%s?%s' % (id, urllib.urlencode(self.__sargs))
        print(self.__url)
        self.__req = urllib2.Request(self.__url)
        self.__req.add_header('Accept', 'application/json')
        self.__req.lifetime = 3600
        self.__page = urllib2.urlopen(self.__req)
        self.__data = json.load(self.__page)
        self.id = self.__data['id']
        self.title = self.__data['title']
        self.originaltitle = self.__data['original_title']
        self.releasedate = datetime.datetime.strptime(self.__data['release_date'], '%Y-%m-%d').date()
        print(self.__data['release_date'])
        print(type(self.releasedate))
        print('Release date - %s' % self.releasedate)
        self.cast = self.populate_cast()

    def populate_cast(self):
        self.__sargs = {'api_key': api_key}
        self.__url = 'http://api.themoviedb.org/3/movie/%s/casts?%s' % (self.id, urllib.urlencode(self.__sargs))
        self.__req = urllib2.Request(self.__url)
        self.__req.add_header('Accept', 'application/json')
        self.__req.lifetime = 3600
        print(self.__url)
        self.__page = urllib2.urlopen(self.__req)
        self.__data = json.load(self.__page)
        self._cast = []
        for item in self.__data['cast']:
            self._cast.append(Actor(item['id']))
        return self._cast


class Actor:
    def __init__(self, id):
        self.__sargs = {'api_key':api_key}
        self.__url = 'http://api.themoviedb.org/3/person/%s?%s' % (id, urllib.urlencode(self.__sargs))
        self.__req = urllib2.Request(self.__url)
        self.__req.add_header('Accept', 'application/json')
        self.__req.lifetime = 3600
        self.__page = urllib2.urlopen(self.__req)
        self.__data = json.load(self.__page)
        self.name = self.__data['name']
        try:
            self.birthday = datetime.datetime.strptime(self.__data['birthday'], '%Y-%m-%d').date()
        except TypeError:
            self.birthday = None
        print('%s - %s' % (self.name, self.birthday))
