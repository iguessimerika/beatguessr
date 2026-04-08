import data, random

def random_song():
    songs = data.get_songs()
    
    rdm_number = random.randint(0, len(songs)-1)
    
    return songs[rdm_number]

def build_song_structure(artists, songs):
    structure = {}
    artist_structure = {}
    
    for artist in artists:
        name = artist['name']
        artist_structure[artist['artistid']] = name
        structure[name] = []
    
    for song in songs:
        title = song['title']
        artist_id = song['artist_id']
        artist_name = artist_structure[artist_id]
                
        structure[artist_name].append(title)
    
    return structure

def get_hints(songid):
    hints = {}
    hints_db = data.get_song_hints(songid)
    
    for hint in hints_db:
        hints[hint['hint_number']] = hint['hint_text']
    
    return hints

def build_highscore_structure(user_id):
    songs = data.get_user_songs(user_id)

    print(songs)

    structure = {}
    
    for song in songs:
        songid = song['song_id']
        title = song['name'] + " - " + song['title']
        song_guesses = dict(data.get_song_guesses(songid))

        for username in song_guesses:
            time = song_guesses[username]

            if title not in structure:
                structure[title] = []
    
            structure[title].append({
                "username": username,
                "time": time
            })

    return structure
    