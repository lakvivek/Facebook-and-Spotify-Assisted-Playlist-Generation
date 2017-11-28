import os
import sys
import glob
import time
import datetime
import numpy as np
import sqlite3

def encode_string(s):
	return "'" + s.replace("'", "''") + "'"

def create_db(filename):
    
    # Create db file and an empty table inside it.

    conn = sqlite3.connect(filename)

    c = conn.cursor()
    q = 'CREATE TABLE songs (track_id text PRIMARY KEY, '
    q += 'title text, song_id text, '
    q += 'release text, artist_id text, artist_mbid text, artist_name text, '
    q += 'loudness float, tempo float, artist_familiarity,'
    q += 'artist_hotttnesss float, energy float)'
 
    c.execute(q)

    conn.commit()
    c.close()
    conn.close()

def fill_from_h5(conn, h5path, verbose=0):
    
    # Inserting data from .h5 file into the new table.
    
    h5 = open_h5_file_read(h5path)
    c = conn.cursor()
    # build query
    q = 'INSERT INTO songs VALUES ('
    track_id = get_track_id(h5)
    q += encode_string(track_id)
    title = get_title(h5)
    q += ', ' + encode_string(title)
    song_id = get_song_id(h5)
    q += ', ' + encode_string(song_id)

    release = get_release(h5)
    q += ', ' + encode_string(release)
    
    artist_id = get_artist_id(h5)
    q += ', ' + encode_string(artist_id)
    artist_mbid = get_artist_mbid(h5)
    q += ', ' + encode_string(artist_mbid)
    artist_name = get_artist_name(h5)
    q += ', ' + encode_string(artist_name)

    loudness = get_loudness(h5)
    q += ", " + str(loudness) if not np.isnan(loudness) else ",-1"
    tempo = get_tempo(h5)
    q += ", " + str(tempo) if not np.isnan(tempo) else ",-1"

    artist_familiarity = get_artist_familiarity(h5)
    q += ", " + str(artist_familiarity) if not np.isnan(artist_familiarity) else ",-1"

    artist_hotttnesss = get_artist_hotttnesss(h5)
    q += ", " + str(artist_hotttnesss) if not np.isnan(artist_hotttnesss) else ",-1"

    energy = get_energy(h5)
    q += ", " + str(energy) if not np.isnan(energy) else ",-1"

    h5.close()
    q += ')'
  
    c.execute(q)
    conn.commit() 
    c.close()

def add_indices_to_db(conn, verbose=0):
	c = conn.cursor()
	# index to search by (artist_id) or by (artist_id,release)
	q = "CREATE INDEX idx_artist_id ON songs ('artist_id','release')"
	if verbose > 0:
	    print q
	c.execute(q)
	# index to search by (artist_mbid) or by (artist_mbid,release)
	q = "CREATE INDEX idx_artist_mbid ON songs ('artist_mbid','release')"
	if verbose > 0:
	    print q
	c.execute(q)

	# index to search by (artist_name)
	# or by (artist_name,title) or by (artist_name,title,release)
	q = "CREATE INDEX idx_artist_name ON songs "
	q += "('artist_name','title','release')"

	c.execute(q)
	# index to search by (title)
	# or by (title,artist_name) or by (title,artist_name,release)
	q = "CREATE INDEX idx_title ON songs ('title','artist_name','release')"
	if verbose > 0:
	    print q
	c.execute(q)
	# index to search by (release)
	# or by (release,artist_name) or by (release,artist_name,title)
	q = "CREATE INDEX idx_release ON songs ('release','artist_name','title')"
	if verbose > 0:
	    print q

def die_with_usage():
    print 'Please run the script in following way:'
    print '   python generate_songs_feature_database.py path/to/MillionSongSubset/data filenameForDB.db'
    sys.exit(0)


if __name__ == '__main__':

    # Parameters not provided
    if len(sys.argv) < 3:
        die_with_usage()

    pythonsrc = os.path.join('/Users/saurabhghotane/SG_Data/CMPE_256_Project/',sys.argv[0])
    pythonsrc = os.path.abspath(pythonsrc)

    sys.path.append(pythonsrc)

    from hdf5_getters import *

 	# read parameters
    maindir = os.path.abspath(sys.argv[1])
    dbfile = os.path.abspath(sys.argv[2])

    # Check if path exists
    if not os.path.isdir(maindir):
        print 'ERROR: %s is not a directory.' % maindir

    # Check if DB file already exists
    if os.path.exists(dbfile):
        print 'ERROR: %s already exists! delete or provide a new name' % dbfile
        sys.exit(0)

    # start time
    t1 = time.time()

    # create the database
    create_db(dbfile)

    # open a new connection
    conn = sqlite3.connect(dbfile)

    verbose = 0

    # Loop through the HDF5 files
    cnt_files = 0
    for root, dirs, files in os.walk(maindir):
        files = glob.glob(os.path.join(root, '*.h5'))
        for f in files:
            fill_from_h5(conn, f, verbose=verbose)
            cnt_files += 1
            if cnt_files % 200 == 0:
                conn.commit()
    conn.commit()
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2 - t1))
    print 'added the content of', cnt_files, 'files to database:', dbfile
    print 'Time Taken:', stimelength

    # add indices
    c = conn.cursor()
    res = c.execute('SELECT Count(*) FROM songs')
    nrows_before = res.fetchall()[0][0]
    add_indices_to_db(conn, verbose=verbose)
    res = c.execute('SELECT Count(*) FROM songs')
    nrows_after = res.fetchall()[0][0]
    c.close()
    
    print 'Inserted ', nrows_after, 'rows.'
    
    # close connection
    conn.close()

    # end time
    t3 = time.time()

    # DONE
    print 'Done! Database Created:', dbfile
    stimelength = str(datetime.timedelta(seconds=t3 - t1))
    print 'Total execution time:', stimelength


