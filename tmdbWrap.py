import datetime
import urllib
import urllib2
import json

class tmdbWrap:
    # This is the unique API key for TMDb given to each developer; this
    # particular one belongs to Mikhail Lepilov.
    api_key = 'a1c96b8cef6c9961330b81bd8a508376'
    movielist = []

    def __init__(self, query):
        self.__sargs = {'api_key':self.api_key, 'query':query, 'include_adult':False}
        self.__url = 'http://api.themoviedb.org/3/search/movie?%s' % urlencode(sargs)
        self.__page = urllib2.request(self.__url)
        self.__page.add_header('Accept', 'application/json')
        self.__page.lifetime = 3600
        self.__data = json.loads(self.__page.open())
        for item in self.__data['results']
            self.movielist.append(Movie(item))


class Movie:
    def __init__(self, id):
        self.__sargs = {'api_key':api_key}
        self.__url = 'http://api.themoviedb.org/3/movie/', id, '/%s' % urlencode(self.__sargs)
        self.__page = urllib2.request(self.__url)
        self.__page.add_header('Accept', 'application/json')
        self.__page.lifetime = 3600
        self.__data = json.loads(self.__page.open())
        self.id = self.__data['id']
        self.title = self.__data['title']
        self.originaltitle = self.__data['original_title']
        self.releasedate = datetime.strptime(self.__data['release_date'], '%y-%m-%d')
        self.cast = populate_cast()

    def populate_cast(self)
        self.__sargs = {'api_key': api_key}
        self.__url = 'http://api.themoviedb.org/3/movie/', self.id, '/cast?%s' % urlencode(self.__sargs)
        self.__page = urllib2.request(self.__url)
        self.__page.add_header('Accept', 'application/json')
        self.__page.lifetime = 3600
        self.__data = json.loads(self.__page.open())
        self._cast = []
        for item in self.__data['cast']
            self._cast.append(Actor(item['id']))
        return self._cast


class Actor:
    def __init__(self, id):
        self.__sargs = {'api_key':api_key}
        self.__url = 'http://api.themoviedb.org/3/person/', id, '?%s' % urlencode(sargs)
        self.__page = urllib2.request(self.__url)
        self.__page.add_header('Accept', 'application/json')
        self.__page.lifetime = 3600
        self.__data = json.loads(self.__page.open())
        self.name = self.__data['name']
        self.birthday = datetime.strptime(self.__data['birthday'], '%y-%m-%d')
