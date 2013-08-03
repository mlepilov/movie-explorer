# This file contains the tmdb wrapper and associated classes used by
# movie-explorer.py.

import datetime
import urllib
import urllib2
import json

# TODO: make the wrapper not populate the cast on init, but rather after the
# user selects the movie (otherwise program is too slow)
# TODO: handle multiple pages of movie results
# TODO: handle a lot of results properly (i.e. by saying so and refusing)

class tmdbData:
    # This is the unique API key for TMDb given to each developer; this
    # particular one belongs to Mikhail Lepilov.
    api_key = 'a1c96b8cef6c9961330b81bd8a508376'
    base_url = 'http://api.themoviedb.org/3/'
    base_args = {'api_key': api_key}
    data = None

    def __init__(self, url, **kargs):
        self._args = dict(self.base_args, **kargs)
        self._url = '%s%s%s' % (self.base_url, url, urllib.urlencode(self._args))
        self._req = urllib2.Request(self._url)
        print(self._url)
        self._req.add_header('Accept', 'application/json')
        self._req.lifetime = 3600
        try:
            self._page = urllib2.urlopen(self._req)
        except HTTPError:
            raise TmdbError(1)
        else:
            try:
                self._data = json.load(self._page)
            except ValueError:
                raise TmdbError(3)
            else:
                if 'status_code' in self._data:
                    if self._data['status_code'] == 7:
                        raise TmdbError(2)
                    elif self._data['status_code'] == 6:
                        raise TmdbError(4)
                else:
                    self.data = self._data


class tmdbWrap:
    movielist = []

    def __init__(self, query):
        try:
            self._returned = tmdbData('search/movie?', query=query, include_adult=False)
        except TmdbError:
            raise
        else:
            for item in self._returned.data['results']:
                self.movielist.append(Movie(item['id']))


class Movie:
    id = None
    title = None
    originaltitle = None
    releasedate = None
    cast = []

    def __init__(self, id):
        try:
            self._returned = tmdbData('movie/%s?' % id)
        except TmdbError:
            raise
        else:
            self.id = self._returned.data['id']
            self.title = self._returned.data['title']
            self.originaltitle = self._returned.data['original_title']
            try:
                self.releasedate = datetime.datetime.strptime(self._returned.data['release_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                self.releasedate = None
            try:
                self.cast = self.populate_cast()
            except TmdbError:
                raise
            
    def populate_cast(self):
        self._cast = []
        try:
            self._returned = tmdbData('movie/%s/casts?' % self.id)
        except TmdbError:
            raise
        else:
            for item in self._returned.data['cast']:
                self._cast.append(Person(item['id']))
        return self._cast


class Person:
    name = None
    birthday = None

    def __init__(self, id):
        try:
            self._returned = tmdbData('person/%s?' % id)
        except TmdbError:
            raise
        else:
            self.name = self._returned.data['name']
            try:
                self.birthday = datetime.datetime.strptime(self._returned.data['birthday'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                self.birthday = None


class TmdbError(Exception):
    errors = { 1: 'Cannot establish a connection to TMDb.',
               2: 'Cannot get data: invalid API key.',
               3: 'Cannot get data: invalid request.',
               4: 'Cannot get data: invalid ID.' }

    def __init__(self, error):
        self.error = error

    def __str(self):
        return repr(errors(self.error))
