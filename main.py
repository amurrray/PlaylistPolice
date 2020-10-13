import pickle
from pathlib import Path
import spotipy
from secrets import CLIENT_ID, CLIENT_SECRETS, REDIRECT_URL, USERNAME, WHITELISTED_USERS

def getToken():
    scope = 'user-read-playback-state user-modify-playback-state playlist-read-collaborative playlist-modify-private playlist-modify-public playlist-read-private'
    return spotipy.util.prompt_for_user_token(USERNAME, scope, client_id=CLIENT_ID,
                                              client_secret=CLIENT_SECRETS, redirect_uri=REDIRECT_URL)

def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

if __name__ == "__main__":
    token=getToken()
    sp = spotipy.Spotify(auth=token)
    current = sp.current_playback()

    # inputPlaylistURI = input("input spotify playlist URI: ")
    # inputPlaylistURI = 'spotify:playlist:3yQnagTU5X4V2HoFSA2gv6' #lithium
    inputPlaylistURI = 'spotify:playlist:7AMG51HALKtdLiInJUIuiO' #collab test
    # inputPlaylistURI = 'spotify:playlist:2JIEJ8sxLJfBC8YSGznJVk' #non-collab test
    
    # gets playlist data
    playlistTracks = get_playlist_tracks(USERNAME,inputPlaylistURI)
    results = sp.playlist(inputPlaylistURI)
        
    # checks if playlist is backed up
    try:
        pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'rb'))

    except FileNotFoundError:
        pickle.dump([], open('/playlist' + str(results['id']) + '.pkl', 'wb')) 

    # checks if collaborative playlist
    if results['collaborative'] == True:
        print('playlist found')
        print(results['name'] + ' - ' + str(len(playlistTracks)) + ' songs')
        
        # finds and removes songs added by non-whitelisted users
        for i in playlistTracks:
            if i['added_by']['id'] in WHITELISTED_USERS:
                pass
            else:
                trackURI = i['track']['uri']
                trackAdder = i['added_by']['id']
                trackName = str(i['track']['name']) + ' - ' + str(i['track']['artists'][0]['name'])
                print(trackName + ' - ' + trackURI + ' - ' + trackAdder)
                trackArray=[trackURI]
                sp.user_playlist_remove_all_occurrences_of_tracks(user=trackAdder, playlist_id=inputPlaylistURI, tracks=trackArray)
                print('\"' + trackName + '\" that was added by \"' + trackAdder + '\" was removed')

        # builds dictionary with the most recent list of tracks
        updatedPlaylistTracks = get_playlist_tracks(USERNAME,inputPlaylistURI)
        i=0
        trackDict= {}
        for track in updatedPlaylistTracks:
            trackDict["id{0}".format(i)] = [track['track']['name'], track['track']['artists'][0]['name'], track['track']['uri'], track['added_by']['id']]
            i+=1
        
        # time to compare new filtered playlist with the old copy
        oldtrackDict = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'rb'))

        if len(oldtrackDict) / 2 >= len(trackDict):
            # playlist has lost more half of its songs

            # list of old tracks
            trackList = []
            for track in oldtrackDict:
                trackList.append(oldtrackDict[track][2])

            # list of new tracks
            newestTrackList = []
            for track in trackDict:
                newestTrackList.append(trackDict[track][2])

            for track in newestTrackList:
                trackList.remove(track)
            
            sp.user_playlist_add_tracks(USERNAME, inputPlaylistURI, trackList)
        
        else:
            # playlist has more than half of its songs
            pass                    

        # updates and saves the dictionary
        updatedPlaylistTracks = get_playlist_tracks(USERNAME,inputPlaylistURI)
        i=0
        trackDict= {}
        for track in updatedPlaylistTracks:
            trackDict["id{0}".format(i)] = [track['track']['name'], track['track']['artists'][0]['name'], track['track']['uri'], track['added_by']['id']]
            i+=1

        print('dictionary built...')
        pickle.dump(trackDict, open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'wb'))
        print('dictionary saved...')

    else:
        print('not a collaborative playlist')



# to view dict
# trackDict = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'rb'))
# print(trackDict)  