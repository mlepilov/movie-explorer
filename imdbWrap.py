# This file contains the IMDb wrapper and associated classes used by the
# movie-explorer module, a part of movie-explorer.
#
# movie-explorer - Search for and display movie information.
# Copyright (C) 2013 Mikhail Lepilov
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# For questions or concerns, contact Mikhail Lepilov at mlepilov@gmail.com
#
# This product uses the TMDb API but is not endorsed or certified by TMDb.

import urllib
import urllib2
import HTMLParser

import utils

# TODO: Make the imdb_scrape*() functions return ValueErrors when data cannot
# be scraped
# TODO: Clean up some string code

class SearchParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'total_results':0, 'results': [] }
        self._result = False
        self._table = False
        self._left = False
        self._leftright = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if self._result == True and tag == 'a':
            self._split1 = attrs[0][1].split('/title/')
            self._split2 = self._split1[1].split('/')
            self.data['results'].append({'id': self._split2[0] })
            self._result = False
        if self._table == True and tag == 'td' and \
          attrs == [('class', 'title')]:
            self._result = True
        if tag == 'table' and attrs == [('class', 'results')]:
            self._table = True

        if self._leftright == True and tag == 'div' and \
          attrs == [('id', 'left')]:
            self._left = True
        if tag == 'div' and attrs == [('class', 'leftright')]:
            self._leftright = True

    def handle_endtag(self, tag):
        if self._left == True and tag == 'div':
            self._left = False

    def handle_data(self, data):
        if self._left == True:
            self._split1 = data.split(' of ')
            self._split2 = self._split1[-1].split('titles')
            self._total_results = \
              int(self._split2[0].replace('\n', '').replace(',', ''))
            self.data.update({'total_results': self._total_results })


class MovieParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'title':'', 'release_date':'' }
        self._name = False
        self._name1 = True
        self._meta = True
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'span' and \
          attrs == [('class', 'itemprop'), ('itemprop', 'name')]:
            self._name = True

        if self._meta == True and tag == 'meta' and \
          attrs[0] == ('itemprop', 'datePublished'):
            self._meta = False
            self.data.update({'release_date': attrs[1][1]})

    def handle_data(self, data):
        if self._name == True and self._name1 == True:
            self._name1 = False
            self.data.update({'title': data})


class CastParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'cast': [] }
        self._table = False
        self._name = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if self._name == True and tag == 'a':
            self._name = False
            self._split1 = attrs[0][1].split('name/')
            self._split2 = self._split1[1].split('/')
            self.data['cast'].append({'id': self._split2[0]})

        if self._table == True and tag == 'td' and \
          attrs == [('class', 'nm')]:
            self._name = True
        
        if tag == 'table' and attrs == [('class', 'cast')]:
            self._table = True

    def handle_endtag(self, tag):
        if self._table == True and tag == 'table':
            self._table == False


class PersonParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.data = { 'name': '', 'birthday': '' }
        self._name = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'h1' and \
          attrs == [('class', 'header'), ('itemprop', 'name')]:
            self._name = True

        if tag == 'time' and \
          ('itemprop', 'birthDate') in attrs:
            self.data.update({'birthday': attrs[1][1]})

    def handle_data(self, data):
        if self._name == True:
            self._name = False
            self.data.update({'name': data.replace('\n','')})


def imdb_scrape_search(page):
    parser = SearchParser()
    parser.feed(page)
    return parser.data


def imdb_scrape_movie(page):
    parser = MovieParser()
    parser.feed(page)
    return parser.data


def imdb_scrape_cast(page):
    parser = CastParser()
    parser.feed(page)
    return parser.data


def imdb_scrape_person(page):
    parser = PersonParser()
    parser.feed(page)
    return parser.data


class imdbData:
    base_url = 'http://www.imdb.com/'

    def __init__(self, id, mode, **kargs):
        if mode == 'search':
            self._args = { 'title': id,
                          'title_type': 'feature,tv_movie,short',
                          'view': 'simple',
                          'count': 20 }
            if 'start' in kargs:
                self._args.update(kargs)
            self._url = '%ssearch/title?%s' % (self.base_url,
                                               urllib.urlencode(self._args))
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_search(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data
        elif mode == 'movie':
            self._url = '%stitle/%s' % (self.base_url, id)
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_movie(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data
        elif mode == 'cast':
            self._url = '%stitle/%s/fullcredits' % (self.base_url, id)
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_cast(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data
        elif mode == 'person':
            self._url = '%sname/%s' % (self.base_url, id)
            self._req = urllib2.Request(self._url)
            try:
                self._sock = urllib2.urlopen(self._req)
                self._html = self._sock.read()
                self._sock.close()
            except urllib2.HTTPError as e:
                raise ImdbError(2)
            except urllib2.URLError as e:
                if e.__class__.__name__ != 'HTTPError':
                    raise ImdbError(1)
            else:
                try:
                    self._data = imdb_scrape_person(self._html)
                except ValueError:
                    self.data = None
                    raise ImdbError(3)
                self.data = self._data


class imdbWrap:
    def __init__(self, query):
        self.query = query
        self.movielist = []
        self.totalresults = 0

        try:
            self._returned = imdbData(query, 'search')
        except ImdbError:
            raise
        else:
            for item in self._returned.data['results']:
                try:
                    self.movielist.append(utils.Movie(item['id'], 'imdb'))
                except ImdbError:
                    raise
            self.totalresults = self._returned.data['total_results']

    def load_next_page(self):
        try:
            self._returned = imdbData(self.query, 'search',
                start=len(self.movielist)+1)
        except ImdbError:
            raise
        else:
            for item in self._returned.data['results']:
                try:
                    self.movielist.append(utils.Movie(item['id'], 'imdb'))
                except ImdbError:
                    raise


class ImdbError(Exception):
    errors = { 1: 'Cannot get data from IMDb: no internet connection.',
               2: 'Cannot get data from IMDb: bad URL specified.',
               3: 'Cannot get data from IMDb: bad data returned.' }

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.errors[self.error]
