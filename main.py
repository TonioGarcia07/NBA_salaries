from bs4 import BeautifulSoup, Comment
import urllib, time, re, csv
from math import ceil

url_nba = "http://www.basketball-reference.com/leagues/NBA_20{:02}_{}.html"
url_player = "http://www.basketball-reference.com/players/{}"
stats = ["totals", "advanced"]
seasons = range(5, 16)

#######################################################################################
###############                                                         ###############
###############     Creation of the total and advanced stat tables      ###############
###############                                                         ###############
#######################################################################################

player_links = {}
for stat in stats:
    players = []
    for season in seasons:
        time.sleep(1)
        print "Parsing season 20{:02}/{:02} for {} stats...".format(season-1, season, stat)
        soup = BeautifulSoup(urllib.urlopen(url_nba.format(season, stat)).read(), "lxml")

        for player_soup in soup.find_all('td', {'data-append-csv':re.compile('.+')}):
            player = {}
            pseudo = player_soup['data-append-csv']
            link = player_soup.parent.find('a')["href"].replace("/players/", '')
            player_links[pseudo] = link
            player['pseudo'] = pseudo
            player['link']   = link
            player['season'] = "{:02}/{:02}".format(season-1, season)

            for el in player_soup.parent.find_all('td', {'data-stat':re.compile('.+')}):
                player[el["data-stat"]] = el.text.replace("\n", '')
            
            players.append(player)

    print "Pouring the data into the file {}.csv...".format(stat)
    with open(stat+'.csv', 'wb') as fout:
        csvout = csv.writer(fout)
        csvout.writerow(players[0].keys())
        for player in players:
            csvout.writerow(player.values())
            

#######################################################################################
###############                                                         ###############
###############         Creation of the last table: salaries            ###############
###############                                                         ###############
#######################################################################################

players = []
cont = 0
for pseudo, link in player_links.items():
    player = {}
    time.sleep(0.1)
    print 'Player {}: {} of {}...'.format(pseudo, cont, len(player_links.keys()))
    soup_stat = BeautifulSoup(urllib.urlopen(url_player.format(link)).read(), "lxml")

    ########################################################### Salary
    try:
        soup_season = soup_stat.find('div', {'id':'all_all_salaries'})
        comments = soup_season.findAll(text=lambda text:isinstance(text, Comment))
        soup_comment = BeautifulSoup(comments[0], 'lxml')
        for ss in seasons:
            season_text = "20{:02}-{:02}".format(ss-1, ss)
            for soup_salary in soup_comment.find_all('td', {'data-stat':'salary'}):
                if season_text in soup_salary.parent.find('th').text:
                    player['salary{:02}'.format(ss)] = soup_salary.text
                break
                    
    except Exception, e:
        print e, "Filling salary with None..."
        for ss in seasons:
            player['salary{:02}'.format(ss)] = None
        
    cont += 1
    players.append(player)

    ############################################# Save every 250 iterations
    if cont % 250 == 0 or cont == len(player_links.keys()):
        print "Pouring the data into the file stats.csv..."
        with open('stats{}.csv'.format(int(ceil(cont/200))), 'wb') as fout:
            csvout = csv.writer(fout)
            
            headers = players[0].keys()
                    
            csvout.writerow(headers)
            for player in players:
                csvout.writerow(player.values())
            players = []
