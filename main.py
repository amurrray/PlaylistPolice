import time
from datetime import datetime, timedelta
from pytz import timezone
import pickle
import requests
from pathlib import Path
import spotipy
from secrets import CLIENT_ID, CLIENT_SECRETS, REDIRECT_URL, USERNAME, WHITELISTED_USERS, PLAYLIST_URI

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getToken():
    scope = 'user-read-playback-state user-modify-playback-state playlist-read-collaborative playlist-modify-private playlist-modify-public playlist-read-private'
    return spotipy.util.prompt_for_user_token(USERNAME, scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRETS, redirect_uri=REDIRECT_URL)

def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def add_playlist_tracks(username,playlist_id,trackList):
    if len(trackList) > 100:
        if len(trackList) / 100 > 1:
            n=0
            print(bcolors.OKCYAN + '------------------------' + bcolors.ENDC)
            print(bcolors.HEADER + 'type A' + bcolors.ENDC)
            for i in (range(int(len(trackList) / 100) + 1)):
                cutTrackList = trackList[n:n+100]
                print(bcolors.OKGREEN + str(i+1) + ' of ' + str(int(len(trackList) / 100) + 1) + bcolors.ENDC)
                print(bcolors.OKGREEN + str(len(trackList)) + ' total songs' + bcolors.ENDC)
                # print(cutTrackList)
                sp.user_playlist_add_tracks(username, inputPlaylistURI, cutTrackList)
                n+=100
                print(bcolors.OKGREEN + 'added ' + str(len(cutTrackList)) + ' songs from backup')
                print(bcolors.OKCYAN + '------------------------' + bcolors.ENDC)

        else:
            n=0
            print(bcolors.OKCYAN + '------------------------' + bcolors.ENDC)
            print(bcolors.HEADER + 'type B' + bcolors.ENDC)
            for i in (range(int(len(trackList) / 100))):
                cutTrackList = trackList[n:n+100]
                print(bcolors.OKGREEN + str(i+1) + ' of ' + str(int(len(trackList) / 100)) + bcolors.ENDC)
                print(bcolors.OKGREEN + str(len(trackList)) + ' total songs' + bcolors.ENDC)
                # print(cutTrackList)
                sp.user_playlist_add_tracks(username, inputPlaylistURI, cutTrackList)
                n+=100
                print(bcolors.OKGREEN + 'added ' + str(len(cutTrackList)) + ' songs from backup' + bcolors.ENDC)
                print(bcolors.OKCYAN + '------------------------' + bcolors.ENDC)


    else:
        print(bcolors.OKCYAN + '------------------------' + bcolors.ENDC)
        print(bcolors.HEADER + 'type C' + bcolors.ENDC)
        # print(trackList)
        print(bcolors.OKGREEN + str(len(trackList)) + ' total songs' + bcolors.ENDC)
        sp.user_playlist_add_tracks(username, inputPlaylistURI, trackList)
        print(bcolors.OKGREEN + 'added ' + str(len(trackList)) + ' songs from backup' + bcolors.ENDC)
        print(bcolors.OKCYAN + '------------------------' + bcolors.ENDC)

token=getToken()
sp = spotipy.Spotify(auth=token)
inputPlaylistURI = PLAYLIST_URI

    while True:    
        playlistTracks = get_playlist_tracks(USERNAME,inputPlaylistURI)
        results = sp.playlist(inputPlaylistURI)
            
        # checks if playlist is backed up
        try:
            pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'rb'))
    
        except FileNotFoundError:
            pickle.dump([], open('playlist' + str(results['id']) + '.pkl', 'wb'))  
    
        # checks if collaborative playlist
        if results['collaborative'] == True:
            # print('playlist found')
            # print(results['name'] + ' - ' + str(len(playlistTracks)) + ' songs')
            
            # finds and removes songs added by non-whitelisted users
            for i in playlistTracks:
                if i['added_by']['id'] in WHITELISTED_USERS:
                    pass
                else:
                    trackURI = i['track']['uri']
                    trackAdder = i['added_by']['id']
                    trackName = str(i['track']['name']) + ' - ' + str(i['track']['artists'][0]['name'])
                    #print(trackName + ' - ' + trackURI + ' - ' + trackAdder)
                    trackArray=[trackURI]
                    sp.user_playlist_remove_all_occurrences_of_tracks(user=trackAdder, playlist_id=inputPlaylistURI, tracks=trackArray)
                    print(bcolors.FAIL + '\"' + trackName + '\" that was added by \"' + trackAdder + '\" was removed' + bcolors.ENDC)
    
            # builds dictionary with the most recent list of tracks
            updatedPlaylistTracks = get_playlist_tracks(USERNAME,inputPlaylistURI)
            i=0
            trackDict= {}
            for track in updatedPlaylistTracks:
                trackDict["id{0}".format(i)] = [track['track']['name'], track['track']['artists'][0]['name'], track['track']['uri'], track['added_by']['id']]
                i+=1
            
            # time to compare new filtered playlist with the old copy
            oldtrackDict = pickle.load(open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'rb'))
    
            if len(oldtrackDict) - len(trackDict) > 25:
                # playlist has lost more than 25 of its songs
    
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

                add_playlist_tracks(USERNAME, inputPlaylistURI, trackList)
            
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
    
            #print('dictionary built...')
            pickle.dump(trackDict, open(str(Path(__file__).resolve().parents[0]) + '/playlist' + str(results['id']) + '.pkl', 'wb'))
            #print('dictionary saved...')
    
        else:
            print('not a collaborative playlist')
        
        est = timezone('EST')
        print(bcolors.OKBLUE + 'filtered @ '+str(datetime.now(est)+timedelta(hours=1)) + bcolors.ENDC)
        time.sleep(300)         
    

if __name__ == "__main__":
    main()