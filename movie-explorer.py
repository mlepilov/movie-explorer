# movie-explorer - Search for and display movie information.
# Copyright (C) 2013 Mikhail Lepilov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# For questions or concerns, contact Mikhail Lepilov at mlepilov@gmail.com

# This product uses the TMDb API but is not endorsed or certified by TMDb.

import datetime
import sys

import tmdbWrap

# The following is a function that calculates the age of an actor, taking as
# input two datetime arguments (date the actor was born and date the movie
# was shot), and giving as output the age as an integer.
#
# Note: the following is a snippet of code inspired by stackoverflow:
# http://stackoverflow.com/questions/2217488/age-from-birthdate-in-python
# Specifically, the inspiration was submitted by the following user:
# http://stackoverflow.com/users/65387/mark
#
# All the fuss is due to handling leap years (ValueError could be better
# handled by checking exactly what the error is, in case some variable is not
# what we expect). Alternatively, we could have just divided by 365.25 days but
# that is less elegant.
def calculate_age(born, shot):
    if born is not None and shot is not None:
        try:
            birthday = born.replace(year=shot.year)
        except ValueError:
            birthday = born.replace(year=shot.year, day=born.day-1)
        if birthday > shot:
            return shot.year - born.year - 1
        else:
            return shot.year - born.year

# The global variable running_age is used to keep a running total of the sum of
# the ages of the cast members. The global variable unaccounted is used to keep
# a running total of the number of cast members we do not have birthday data
# on. Such actors are left out of our average age calculation that we make at
# the end of the script. Note that unaccounted is at most the number of cast
# members in the movie.
running_age = 0
unaccounted = 0

# Here we ask for a title to search for. If no title is given, we exit.
query = raw_input('Search for the title of a film: ')
if query is not '':
    results = tmdbWrap.tmdbWrap(query)
else:
    print('No title given to search for; exiting.')
    sys.exit(1)

# Here we display the results of our search, if it is successful. Note that if
# the search is not successful, we exit. We do type checking here, however
# unpythonic that may be, because it is not documented at all what kind of
# result the tmdb3 module writes as the releasedate of a movie for which such
# information is not available.

# POSSIBLY REMOVE TYPE CHECKING

if len(results.movielist) is not 0:
    print('There is a total of %s result%s matching "%s".' %
          (len(results.movielist), ('s','')[len(results.movielist) is 1], query))
    for i in range(len(results.movielist)):
        if type(results.movielist[i].releasedate) is datetime.date:
            print('[%s] "%s" (%s)' %
                  (i+1, results.movielist[i].title, results.movielist[i].releasedate.year))
        else:
            print('[%s] "%s" (%s)' %
                  (i+1, results.movielist[i].title, 'Unknown'))
else:
    print('No films matching "%s" found; exiting.' % query)
    sys.exit(1)

# Here we disambiguate the results of our search, if it was successful.
currentstr = raw_input('Input the number of the desired film result: ')
try:
    current = int(currentstr)-1
except ValueError:
    current = -1
while current not in range(len(results.movielist)):
    currentstr = raw_input('Invalid film result number entered; try again: ')
    try:
        current = int(currentstr)-1
    except ValueError:
        current = -1
if type(results.movielist[current].releasedate) is datetime.date:
    print('You have selected "%s" (%s).' %
          (results.movielist[current].title, results.movielist[current].releasedate.year))
else:
    print('You have selected "%s" (Unknown).' % (results.movielist[current].title))

# Here we print out the cast members and their ages at the time that the
# selected film was released. This is the place we call the function
# calculate_age, defined above. This is also where we internally keep track
# of and update both the global variables running_age and unaccounted.
if len(results.movielist[current].cast) is 0:
    print('There are no cast data available.')
else:
    print('The following is a list of the cast members with their ages at ' \
          'the time the film was released:')
for i in range(len(results.movielist[current].cast)):
    if type(results.movielist[current].releasedate) is datetime.date:
        age = calculate_age(results.movielist[current].cast[i].birthday,
                            results.movielist[current].releasedate)
    else:
        age = calculate_age(results.movielist[current].cast[i].birthday,
                            None)
    print('%s - Age %s' %
          (results.movielist[current].cast[i].name, (age, 'Unknown')[age is None]))
    if age is not None:
        running_age = running_age + age
    else:
        unaccounted += 1

# Here we calculate the average age and print it out, if we have enough data.
# The reason why we are fussing around with round() and multiplying by 1.0 is
# that we probably want the average age rounded to the first decimal place,
# seeing as we have one significant figure to work with.
if len(results.movielist[current].cast) - unaccounted is not 0:
    average_age = round(
        (running_age*1.0) / (len(results.movielist[current].cast)-unaccounted), 1)
    print('The average age of the cast in this film is %s.' % average_age)
else:
    print('There are not enough data to determine the average age of the cast.')
