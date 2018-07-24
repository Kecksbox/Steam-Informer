import os.path
import requests

blacklist_games = 'blacklist-games' + '.txt'
done_games = 'done-games' + '.txt'

def check_for_file():
    if not os.path.exists('./' + blacklist_games):
        file = open(blacklist_games, 'w')
        file.close()

    if not os.path.exists('./' + done_games):
        file = open(done_games, 'w')
        file.close()

def add_game_as_done(game_id):
    with open(done_games, 'w') as file:
        file.write(game_id + '\n')

def get_game():
    #Check if the save files exits and if not, create them
    check_for_file()

    #Get the apps via the steam api
    all_apps_url = 'http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json'
    app_detail_url = 'http://store.steampowered.com/api/appdetails?appids='

    steam_params = dict(
        origin='Chicago,IL',
        destination='Los+Angeles,CA',
        waypoints='Joplin,MO|Oklahoma+City,OK',
        sensor='false'
    )

    steam_apps = requests.get(url=all_apps_url, params=steam_params).json()

    counter = 0

    for app in steam_apps['applist']['apps']:
        #Check if the app we are looking at, is in the blacklisted list
        if str(app['appid']) in open(blacklist_games).read():
            continue

        counter += 1
        print(str(counter))

        # Check if the app we are looking at, is in the blacklisted list
        if str(app['appid']) in open(done_games).read():
            continue

        #Get the detailed app information
        app_detailed_info = requests.get(url=app_detail_url + str(app['appid']), params=steam_params).json()

        # Check if we were able to get the detailed app info
        if app_detailed_info[str(app['appid'])]['success'] == False:
            with open(blacklist_games, 'w') as file:
                file.write(str(app['appid']) + '\n')
            continue

        #Shorten the info
        app_detailed_info = app_detailed_info[str(app['appid'])]['data']

        # Check if the app is a game
        if not app_detailed_info['type'] == 'game':
            with open(blacklist_games, 'w') as file:
                file.write(app['appid'] + '\n')
            continue

        return app['appid']

    return -1