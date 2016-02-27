from bs4 import BeautifulSoup
import urllib2
import re
import pandas as pd

def clean_data(df):
    df['OR'] = df['OR'].map(lambda x: re.sub(',','',x))
    df['OP'] = df['OP'].map(lambda x: re.sub(',','',x))
    df['GR'] = df['GR'].map(lambda x: re.sub(',','',x))
    df['TV'] = df['TV'].map(lambda x : x[1:])
    df['TV'] = df['TV'].map(lambda x : x.rstrip('m'))
    df['TV'] = df['TV'].map(lambda x : float(x))
    return df

class ScrapeData():
    def __init__(self, league_id):
        self.league_id = league_id

    def scrape_league_info(self):
        url = 'http://fantasy.premierleague.com/my-leagues/{}/standings/'.format(self.league_id)

        raw_league_data = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")

        all_teams_metadata = []

        for row in raw_league_data('table')[0].findAll('tr')[1:]:
            tds = row('td')
            id_str = (str(tds[2].a))
            try:
                team_id = re.search('entry/(.+?)/event', id_str).group(1)
            except AttributeError:
                # id not found
                team_id = '' # apply your error handling

            team_name = tds[2].string
            player_name = tds[3].string

            team_info = {
                "player_name": player_name,
                "team_name": team_name,
                "team_id": team_id
            }

            all_teams_metadata.append(team_info)

        return all_teams_metadata

    def scrape_team_data_from_league_info(self, all_teams_metadata):

        all_teams_data = []

        for teams in all_teams_metadata:
            url = 'http://fantasy.premierleague.com/entry/{}/history/'.format(teams["team_id"])

            raw_team_data = BeautifulSoup(urllib2.urlopen(url).read(), "lxml")

            player_data = []


            for row in raw_team_data('table')[0].findAll('tr')[1:]:
                tds = row('td')
                data = {
                    'ID': teams["team_id"],
                    'GW': tds[0].string,
                    'GP': tds[1].string,
                    'PB': tds[2].string,
                    'GR': tds[3].string,
                    'TM': tds[4].string,
                    'TC': tds[5].string,
                    'TV': tds[6].string,
                    'OP': tds[7].string,
                    'OR': tds[8].string,
                    'player_name': teams["player_name"],
                    'team_name': teams["team_name"],
                }
                player_data.append(data)

            all_teams_data.extend(player_data)

        return all_teams_data

    def convert_data_to_dataframe(self, all_teams_data):
        df = pd.DataFrame.from_records(all_teams_data)
        df = clean_data(df)
        return df
    
    def get_data(self):
        all_teams_metadata = self.scrape_league_info()
        all_teams_data = self.scrape_team_data_from_league_info(all_teams_metadata)
        team_data_df = self.convert_data_to_dataframe(all_teams_data)
        return team_data_df

def main():
    league = ScrapeData(314488)
    data = league.get_data()
    print data


if __name__ == '__main__':
    main()
    