import requests
from bs4 import BeautifulSoup
import pandas as pd
import re




def extract_year(url):
    match = re.search(r'boxscores/(\d{4})', url)
    return match.group(1) if match else 'Unknown'



def scrape_table(url, table_id, description):
    print(f"Scraping {description} from: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': table_id})
    data = []
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            data.append(cols)
    else:
        print(f"No {description} data found.")
    return data



def scrape_game_info(url):
    print(f"Scraping Game Info from: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    game_info = soup.find('div', {'class': 'scorebox_meta'})
    game_data = [["Year", extract_year(url)]]

    if game_info:
        rows = game_info.find_all('div')
        for row in rows:
            text = row.text.strip()
            game_data.append([text])


            if "Time of Possession" in text:
                game_data.append(["Time of Possession", text.split(':')[-1].strip()])
            if "Turnovers" in text:
                game_data.append(["Turnovers", text.split(':')[-1].strip()])
    else:
        print("No Game Info data found.")
    return game_data



data_sources = [
    {"url": "https://www.pro-football-reference.com/boxscores/202409120mia.htm#all_expected_points",
     "table_id": "all_expected_points", "desc": "Expected Points Added"},
    {"url": "https://www.pro-football-reference.com/boxscores/202409230buf.htm#all_vis_drives",
     "table_id": "vis_drives", "desc": "Average Points by Drives"},
    {"url": "https://www.pro-football-reference.com/boxscores/202409120mia.htm#all_team_stats",
     "table_id": "team_stats", "desc": "Team Stats"},
    {"url": "https://www.pro-football-reference.com/boxscores/202409080buf.htm", "table_id": "passing_advanced",
     "desc": "Advanced Passing Stats"},
    {"url": "https://www.teamrankings.com/nfl/trends/ats_trends/", "table_id": "", "desc": "ATS Trends"},
    {"url": "https://www.teamrankings.com/nfl/ranking/schedule-strength-by-other", "table_id": "",
     "desc": "Schedule Strength"},
    {"url": "https://www.teamrankings.com/nfl/trend/win_trends/is_home_dog", "table_id": "",
     "desc": "Win Trends - Home Underdog"},
    {"url": "https://www.espn.com/nfl/matchup/_/gameId/401671617", "table_id": "", "desc": "Matchup Info"}
]


with pd.ExcelWriter('NFL_Data_Scraped.xlsx', engine='xlsxwriter') as writer:
    for source in data_sources:
        scraped_data = scrape_table(source["url"], source["table_id"], source["desc"])
        if scraped_data:
            df = pd.DataFrame(scraped_data)
            df.insert(0, "Year", extract_year(source["url"]))  # Add year column
            df.to_excel(writer, sheet_name=source["desc"].replace(" ", "_"), index=False)
        else:
            print(f"No {source['desc']} data to write.")


    game_info_url = "https://www.pro-football-reference.com/boxscores/202409120mia.htm"
    game_info_data = scrape_game_info(game_info_url)
    if game_info_data:
        df_game_info = pd.DataFrame(game_info_data)
        df_game_info.to_excel(writer, sheet_name='Game_Info', index=False)
    else:
        print("No Game Info data to write.")

print("Data has been successfully written to Excel!")