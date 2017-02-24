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
    player['pseudo'] = pseudo
    time.sleep(0.1)
    print 'Player {}: {} of {}...'.format(pseudo, cont, len(player_links.keys()))
    soup_stat = BeautifulSoup(urllib.urlopen(url_player.format(link)).read(), "lxml")

    ########################################################### Salary
    for ss in seasons:
        player['salary{:02}'.format(ss)] = None
        
    try:
        soup_season = soup_stat.find('div', {'id':'all_all_salaries'})
        comments = soup_season.findAll(text=lambda text:isinstance(text, Comment))
        soup_comment = BeautifulSoup(comments[0], 'lxml')
        for ss in seasons:
            season_text = "20{:02}-{:02}".format(ss-1, ss)
            for soup_salary in soup_comment.find_all('td', {'data-stat':'salary'}):
                if season_text in soup_salary.parent.find('th').text:
                    player['salary{:02}'.format(ss)] = soup_salary.text
                    
    except Exception, e:
        print e, "Filling salary with None..."


    ############################### Additional time-invariant information
    soup_info = soup_stat.find('div', {'class':'players'})
    player['college'] = None
    player['shoots'] = None
    player['debut'] = None
    player['height'] = None
    player['weight'] = None
    try:
        for tag_p in soup_info.find_all('p'):
            ########## College
            try:
                if "College" in tag_p.text:
                    college = tag_p.find('a').text
                    player['college'] = college
            
            except Exception, e:pass


            ########## Shoots
            try:
                if "Shoots" in tag_p.text:
                    shoots = str(tag_p.contents[-1])
                    player['shoots'] = shoots.replace(" ","").replace("\n","")
            
            except Exception, e:pass

        
            ########## NBA debut
            try:
                if "NBA Debut" in tag_p.text:
                    debut = tag_p.find('a').text
                    player['debut'] = debut[-4:]
            
            except Exception, e:pass


            ########## Height and Weight
            try:
                for soup_span in tag_p.find('span', {'itemprop': 'height'}):
                    height = tag_p.contents[-1].split('cm')[0][-3:]
                    weight = tag_p.contents[-1].split('kg')[0][-3:].replace(u'\xa0', u'')
                    player['height'] = height
                    player['weight'] = weight
            
            except Exception, e:pass

    except Exception, e:pass
    
    cont += 1
    players.append(player)

    ############################################# Save every 250 iterations
    if cont % 250 == 0 or cont == len(player_links.keys()):
        print "Pouring the data into the file stats.csv..."
        with open('stats{}.csv'.format(int(ceil(cont/250))), 'wb') as fout:
            csvout = csv.writer(fout)
            
            headers = players[0].keys()
                    
            csvout.writerow(headers)
            for player in players:
                csvout.writerow(player.values())
            players = []



#######################################################################################
###############                                                         ###############
###############           Concatenation of the tables salary            ###############
###############                                                         ###############
#######################################################################################

res = []
for i in range(1, 5):
    with open('stats{}.csv'.format(i), 'rb') as fin:
        cont = fin.readlines()
        if i==1: res.append(cont[0])
        for el in cont[1:]:
            res.append(el)

with open('salaries.csv', 'wb') as fout:
    for row in res:
        fout.write(row)

