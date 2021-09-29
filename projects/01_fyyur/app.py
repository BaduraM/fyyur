#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify
)
import logging
from logging import (
  Formatter, 
  FileHandler
)
from flask_wtf import Form
from forms import *
from models import (
  Venue, 
  Artist, 
  Show, 
  app, 
  db
)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  mydata = []
  for row in Venue.query.with_entities(Venue.city, Venue.state).distinct().all():
    myvdata = []
    for vrow in Venue.query.filter(Venue.city==row.city, Venue.state==row.state).all():
      tempdata = {"id" : vrow.id,
                  "name" : vrow.name,
                  "num_upcoming_shows" : Show.query.filter(Show.venue_id==vrow.id).count()}
      myvdata.append(tempdata)
    vtext = { "city": row.city, 
              "state": row.state}
    vtext["venues"] = myvdata
    mydata.append(vtext)
  data = mydata
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    vquery = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term', '') + '%'))
    response = {"count" : vquery.count()}
    myvdata = []
    for vrow in vquery.all():
      tempdata = {"id" : vrow.id,
                  "name" : vrow.name,
                  "num_upcoming_shows" : Show.query.filter(Show.venue_id==vrow.id).count()}
      myvdata.append(tempdata)
    response["data"] = myvdata
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  vquery = Venue.query.filter(Venue.id==venue_id)
  for vrow in vquery.all():
    gnr = list(vrow.genres.split(",")) 
    squery = Show.query.join(Artist).filter(Show.venue_id==vrow.id, Show.start_time < db.func.now()).add_columns(Show.id, Show.start_time, (Artist.id).label('artist_id'), (Artist.name).label('artist_name'), (Artist.image_link).label('artist_image_link'))
    pcount = squery.count()
    mysdata = []
    for srow in squery.all():
      stime = srow.start_time.strftime('%Y-%m-%d') + 'T' + srow.start_time.strftime('%H:%M:%S') + '.000Z'
      tempdata = {"artist_id" : srow.artist_id,
                  "artist_name" : srow.artist_name,
                  "artist_image_link" : srow.artist_image_link,
                  "start_time": stime}
      mysdata.append(tempdata)
    uquery = Show.query.join(Artist).filter(Show.venue_id==vrow.id, Show.start_time >= db.func.now()).add_columns(Show.id, Show.start_time, (Artist.id).label('artist_id'), (Artist.name).label('artist_name'), (Artist.image_link).label('artist_image_link'))
    ucount = uquery.count()
    myudata = []
    for srow in uquery.all():
      stime = srow.start_time.strftime('%Y-%m-%d') + 'T' + srow.start_time.strftime('%H:%M:%S') + '.000Z'
      tempdata = {"artist_id" : srow.artist_id,
                  "artist_name" : srow.artist_name,
                  "artist_image_link" : srow.artist_image_link,
                  "start_time": stime}
      myudata.append(tempdata)
    data = {"id": vrow.id,
            "name": vrow.name,
            "address": vrow.address,
            "city": vrow.city,
            "state": vrow.state,
            "phone": vrow.phone,
            "website": vrow.website,
            "facebook_link": vrow.facebook_link,
            "genres": gnr,
            "seeking_talent": vrow.seeking_talent,
            "seeking_description": vrow.seeking_description,
            "image_link": vrow.image_link,
            "past_shows": mysdata,
            "upcoming_shows": myudata,
            "past_shows_count": pcount,
            "upcoming_shows_count": ucount
            }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    print(request)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  for row in Artist.query.all():
    tempdata = {"id" : row.id,
               "name" : row.name}
    data.append(tempdata)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  aquery = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term', '') + '%'))
  response = {"count" : aquery.count()}
  myadata = []
  for row in aquery.all():
    tempdata = {"id" : row.id,
                "name" : row.name,
                "num_upcoming_shows" : Artist.query.filter(Show.artist_id==row.id).count()}
    myadata.append(tempdata)
  response["data"] = myadata
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  aquery = Artist.query.filter(Artist.id==artist_id)
  for arow in aquery.all():
    gnr = list(arow.genres.split(",")) 
    squery = Show.query.join(Venue).filter(Show.artist_id==arow.id, Show.start_time < db.func.now()).add_columns(Show.id, Show.start_time, (Venue.id).label('venue_id'), (Venue.name).label('venue_name'), (Venue.image_link).label('venue_image_link'))
    pcount = squery.count()
    mysdata = []
    for srow in squery.all():
      stime = srow.start_time.strftime('%Y-%m-%d') + 'T' + srow.start_time.strftime('%H:%M:%S') + '.000Z'
      tempdata = {"venue_id" : srow.venue_id,
                  "venue_name" : srow.venue_name,
                  "artist_image_link" : srow.venue_image_link,
                  "start_time": stime}
      mysdata.append(tempdata)
    uquery = Show.query.join(Venue).filter(Show.artist_id==arow.id, Show.start_time >= db.func.now()).add_columns(Show.id, Show.start_time, (Venue.id).label('venue_id'), (Venue.name).label('venue_name'), (Venue.image_link).label('venue_image_link'))
    ucount = uquery.count()
    myudata = []
    for srow in uquery.all():
      stime = srow.start_time.strftime('%Y-%m-%d') + 'T' + srow.start_time.strftime('%H:%M:%S') + '.000Z'
      tempdata = {"venue_id" : srow.venue_id,
                  "venue_name" : srow.venue_name,
                  "venue_image_link" : srow.venue_image_link,
                  "start_time": stime}
      myudata.append(tempdata)
    data = {"id": arow.id,
            "name": arow.name,
            "city": arow.city,
            "state": arow.state,
            "phone": arow.phone,
            "website": arow.website,
            "facebook_link": arow.facebook_link,
            "genres": gnr,
            "seeking_venue": arow.seeking_venue,
            "seeking_description": arow.seeking_description,
            "image_link": arow.image_link,
            "past_shows": mysdata,
            "upcoming_shows": myudata,
            "past_shows_count": pcount,
            "upcoming_shows_count": ucount
            }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  print(form)
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
