from save_games import *
import json; import os

savegame = SaveGame("random_vs_random")




if __name__ == "__main__":
    orangeWins = 0; purpleWins = 0; draws = 0
    with open(savegame.stats_file, "r") as f:
        data = json.load(f)
       
        for item in data:
            if item["winner"] == "Color.ORANGE": 
                orangeWins += 1
            else:
                purpleWins += 1
            for color, score in (item["final_scores"].items()):
                scores = list(item["final_scores"].values())
                if scores[0] == scores[1]:
                    draws += 1

    print(f" Orange wins: {orangeWins}, Purple Wins: {purpleWins}, Ties: {draws}")