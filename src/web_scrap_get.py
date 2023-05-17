import time
from json import JSONDecodeError
import tkinter as tk
from tkinter import ttk

import requests
import random
import time

import random
from fp.fp import FreeProxy


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

class Player:
    def __init__(self, player_id, family_name, given_name, nationality_code, nationality, profile_link, gender,
                 birth_year, rank, points):
        self.player_id = player_id
        self.family_name = family_name
        self.given_name = given_name
        self.nationality_code = nationality_code
        self.nationality = nationality
        self.profile_link = profile_link
        self.gender = gender
        self.birth_year = birth_year
        self.rank = rank
        self.points = points

    def __str__(self):
        return f"{self.rank}. {self.given_name} {self.family_name} ({self.nationality}) - {self.points} points"


def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
    ]
    return random.choice(user_agents)




def get_proxy():
    proxy = FreeProxy(rand=True, timeout=1).get()
    return proxy

print(get_proxy())



def display_players(players):

    def search_utr_ranking():
        selected_item = tree.selection()
        if not selected_item:
            return

        player = None
        for p in players:
            if p.player_id == int(selected_item[0]):
                player = p
                break

        if player is None:
            return

        search_utr_ranking_by_name(f"{player.given_name} {player.family_name}")

    def search_utr_ranking_by_name(player_name):
        query = player_name.replace(' ', '+')
        url = f"https://api.universaltennis.com/v2/search?query={query}&top=10&skip=0&schoolClubSearch=true"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            search_results = response.json()
            # Process the search results as needed
            print(search_results)
        else:
            print(f"Error fetching search results: {response.status_code} - {response.text}")

    def search():
        query = search_query.get()
        selected_field = selected_field_var.get()
        filtered_players = filter_players(players, query, selected_field)
        refresh_tree(filtered_players)

    def filter_players(players, query, selected_field):
        if not query:
            return players

        if selected_field == 'rank':
            if '-' in query:
                start, end = [int(x) for x in query.split('-')]
                return [player for player in players if start <= player.rank <= end]
            else:
                return [player for player in players if str(player.rank) == query]
        else:
            return [
                player for player in players
                if query.lower() in str(getattr(player, selected_field)).lower()
            ]

    def show_all():
        refresh_tree(players)

    def get_unique_nationalities(players):
        return sorted(set(player.nationality for player in players))

    def refresh_tree(filtered_players):
        for i in tree.get_children():
            tree.delete(i)

        for player in filtered_players:
            tree.insert(parent="", index="end", iid=player.player_id, text="",
                        values=(player.rank, player.given_name, player.family_name, player.nationality, player.points))

    def toggle_nationalities():
        new_value = not all(var.get() for var in nationality_vars.values())
        for var in nationality_vars.values():
            var.set(new_value)

    def filter_by_nationality():
        selected_nationalities = [nationality for nationality, var in nationality_vars.items() if var.get()]
        filtered_players = [player for player in players if player.nationality in selected_nationalities]
        refresh_tree(filtered_players)

    root = tk.Tk()
    root.title("ITF Junior Tennis Players")

    search_query = tk.StringVar()
    search_entry = tk.Entry(root, textvariable=search_query)
    search_entry.grid(row=0, column=0)

    selected_field_var = tk.StringVar()
    selected_field_var.set("rank")
    field_names = ["rank", "given_name", "family_name", "nationality", "points"]
    option_menu = tk.OptionMenu(root, selected_field_var, *field_names)
    option_menu.grid(row=0, column=1)

    search_button = tk.Button(root, text="Search", command=search)
    search_button.grid(row=0, column=2)

    show_all_button = tk.Button(root, text="Show All", command=show_all)
    show_all_button.grid(row=0, column=3)

    toggle_button = tk.Button(root, text="Toggle All", command=toggle_nationalities)
    toggle_button.grid(row=0, column=4)

    filter_nationality_button = tk.Button(root, text="Filter by Nationality", command=filter_by_nationality)
    filter_nationality_button.grid(row=0, column=5)

    search_utr_button = tk.Button(root, text="Search UTR Ranking", command=search_utr_ranking)
    search_utr_button.grid(row=0, column=7)

    unique_nationalities = get_unique_nationalities(players)
    nationality_vars = {nationality: tk.BooleanVar(value=False) for nationality in unique_nationalities}

    nationality_frame = tk.Frame(root)
    nationality_frame.grid(row=1, column=6, sticky="nsew")

    nationality_canvas = tk.Canvas(nationality_frame)
    scrollbar = tk.Scrollbar(nationality_frame, orient="vertical", command=nationality_canvas.yview)
    nationality_checkboxes_frame = tk.Frame(nationality_canvas)

    nationality_canvas.configure(yscrollcommand=scrollbar.set)
    nationality_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    nationality_canvas.create_window((0, 0), window=nationality_checkboxes_frame, anchor="nw")
    nationality_checkboxes_frame.bind("<Configure>", lambda e: nationality_canvas.configure(
        scrollregion=nationality_canvas.bbox("all")))

    for i, nationality in enumerate(unique_nationalities):
        checkbox = tk.Checkbutton(
            nationality_checkboxes_frame,
            text=nationality,
            variable=nationality_vars[nationality]
        )
        checkbox.grid(row=i, column=0, sticky="w")

    tree = ttk.Treeview(root)

    tree["columns"] = ("rank", "given_name", "family_name", "nationality", "points")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("rank", anchor=tk.W, width=40)
    tree.column("given_name", anchor=tk.W, width=100)
    tree.column("family_name", anchor=tk.W, width=100)
    tree.column("nationality", anchor=tk.W, width=100)
    tree.column("points", anchor=tk.W, width=100)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("rank", text="Rank", anchor=tk.W)
    tree.heading("given_name", text="Given Name", anchor=tk.W)
    tree.heading("family_name", text="Family Name", anchor=tk.W)
    tree.heading("nationality", text="Nationality", anchor=tk.W)
    tree.heading("points", text="Points", anchor=tk.W)

    for player in players:
        tree.insert(parent="", index="end", iid=player.player_id, text="",
                    values=(player.rank, player.given_name, player.family_name, player.nationality, player.points))

    tree.grid(row=1, column=0, columnspan=7, sticky='nsew')
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.mainloop()


def fetch_players_data(skip, take=10, proxy=None):
    url = "https://www.itftennis.com/tennis/api/PlayerRankApi/GetPlayerRankings"
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
    }

    params = {
        "circuitCode": "JT",
        "playerTypeCode": "B",
        "ageCategoryCode": "",
        "juniorRankingType": "itf",
        "take": take,
        "skip": skip,
        "isOrderAscending": "true"
    }

    retries = 0
    while retries < 10:
        if proxy:
            response = requests.get(url, params=params, headers=headers, proxies={"http": proxy, "https": proxy})
        else:
            response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except JSONDecodeError:
                print("Error decoding JSON, server returned empty or invalid response. Retrying... ({}/{})".format(
                    retries + 1, 10))
                retries += 1
                time.sleep(1)  # Add a delay before retrying
        else:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    print(f"Failed to fetch data after 10 retries")
    return {"items": []}


def main():
    proxy = get_proxy()
    players = []
    skip = 0
    take = 100

    while True:
        try:
            print(f"Fetching players with skip={skip}")
            data = fetch_players_data(skip, take, proxy)
            players_data = data.get("items")

            if skip > 200:
                break
            # if not players_data:
            #   break

            for player_data in players_data:
                player = Player(
                    player_data['playerId'],
                    player_data['playerFamilyName'],
                    player_data['playerGivenName'],
                    player_data['playerNationalityCode'],
                    player_data['playerNationality'],
                    player_data['profileLink'],
                    player_data['gender'],
                    player_data['birthYear'],
                    player_data['rank'],
                    player_data['points']
                )
                players.append(player)
            skip += take
            sleep_time = random.uniform(2, 4)
            time.sleep(sleep_time)

        except Exception as e:
            print(f"Error: {e}")
            # continue # break

    # Print the list of players
    display_players(players)


if __name__ == "__main__":
    main()
