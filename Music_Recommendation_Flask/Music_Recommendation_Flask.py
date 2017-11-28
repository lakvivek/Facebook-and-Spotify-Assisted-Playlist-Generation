from flask import Flask, render_template, request, url_for, redirect
from forms import LoginForm
import pandas as pd
import sqlite3
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

app = Flask(__name__, static_url_path='/static')
app.secret_key = 's3cr3t'


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('index.html', form=form, msg="Please enter details properly")
        else:
            print 'In post else'
            username = form.username.data
            password = form.password.data
            if username == 'admin' and password == 'admin':
                return redirect(url_for('recommend'))
            else:
                return render_template('index.html', form=form, msg="Wrong Credentials")
    elif request.method == 'GET':
        print "In get"
        return render_template('index.html', form=form)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    fb_artists = []
    contents = pd.read_json('templates/fb_data_dump_saurabh.json')
    for current in range(len(contents['music']['data'])):
        fb_artists.append(contents['music']['data'][current]['name'])
    if request.method == 'GET':
        header = "Facebook likes:"
        return render_template('Recommend.html', artists=fb_artists, header=header)
    else:
        header = "Recommendations: "
        conn = sqlite3.connect('output/artist_info.db')
        res = conn.execute("SELECT * FROM artist_info LIMIT 1;")
        data = res.fetchall()
        # print data
        fb_artist_ids = []
        for fb_artist in fb_artists:
            res = conn.execute('SELECT artist_id FROM artist_info where artist_name="%s"' % (fb_artist))
            data = res.fetchall()
            # print fb_artist, data[0][0]
            fb_artist_ids.append(data[0][0])
        simConn = sqlite3.connect('output/final_similarity.db')
        artistSimilarityCounts = {}
        for fb_artist_id in fb_artist_ids:
            if not fb_artist_id in artistSimilarityCounts.keys():
                artistSimilarityCounts[fb_artist_id] = 1
            res = simConn.execute('SELECT * FROM similarity where target="%s"' % (fb_artist_id))
            artistSims = res.fetchall()
            # print len(artistSims)
            for artistSim in artistSims:
                if not artistSim[1] in artistSimilarityCounts.keys():
                    artistSimilarityCounts[artistSim[1]] = 1
                else:
                    artistSimilarityCounts[artistSim[1]] = artistSimilarityCounts[artistSim[1]] + 1
        counter = 0
        RecommendedArtists = []
        for key, value in sorted(artistSimilarityCounts.iteritems(), key=lambda (k, v): (v, k), reverse=True):
            if counter == 12:
                break
            if counter == 4:
                counter = counter + 1
                continue
            # print "%s: %s" % (key, value)
            counter = counter + 1
            res = conn.execute("SELECT artist_name FROM artist_info where artist_id='%s';" % (key))
            data = res.fetchall()
            RecommendedArtists.append(data[0][0])
        tracks = getSpotifyTracks(RecommendedArtists)
        return render_template('Recommend.html', artists=tracks, header=header)
        # print tracks


def getSpotifyTracks(RecommendedArtists):
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False
    for recommendArtist in RecommendedArtists:
        artist = get_artist(recommendArtist, sp)
        if artist:
            tracks = show_recommendations_for_artist(artist, sp)
        else:
            print "Can't find that artist", recommendArtist
    return tracks


def get_artist(name, sp):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None


def show_recommendations_for_artist(artist, sp):
    albums = []
    tracks = []
    results = sp.recommendations(seed_artists = [artist['id']])
    for track in results['tracks']:
        # print track['name'], '-', track['artists'][0]['name']
        track = "%s - %s " %(track['name'], track['artists'][0]['name'])
        tracks.append(track)
    return tracks


if __name__ == '__main__':
    app.run('0.0.0.0')
