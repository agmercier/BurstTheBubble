import csv
import pandas as pd
import random
import numpy as np

# 2915 training posts
# 1957 testing posts


def sample_n_from_csv(
    filename: str, n: int = 100, total_rows: int = 2915
) -> pd.DataFrame:

    skip_rows = random.sample(range(1, total_rows + 1), total_rows - n)
    return pd.read_csv(
        filename, skiprows=skip_rows, encoding="utf8", encoding_errors="ignore"
    )


def sample_n_theme_from_csv(
    filename: str = "StanceDataset\\train.csv",
    n: int = 100,
    total_rows: int = 2915,
    theme: str = "all",
    stance: str = "all",
) -> pd.DataFrame:
    start = 1
    start_found = False
    end = total_rows
    end_found = False
    skip_rows_in_range = []
    skip = []
    all = []
    if (not theme == "all") or (not stance == "all"):
        with open(filename, encoding="utf8", errors="ignore") as file_obj:
            reader_obj = csv.reader(file_obj)
            # skip heading
            heading = next(file_obj)
            for idx, row in enumerate(reader_obj):
                all.append(row)
                if (not theme == "all") and (not theme == row[1]):
                    skip.append(idx)
                if (not stance == "all") and (not stance == row[2]):
                    skip.append(idx)
    possible = list(set(range(1, total_rows)).difference(skip))
    sample_rows = random.sample(possible, n)
    return [x for iter, x in enumerate(all) if iter in sample_rows]


# def data_from_csv(filename: str) -> pd.DataFrame:
#     return pd.read_csv(filename, encoding="utf8", encoding_errors="ignore")


# all_data = data_from_csv("StanceDataset\\train.csv")
# print([all_data["Target"] == "Hillary Clinton"])


def all_targets():
    with open("StanceDataset\\train.csv", encoding="utf8", errors="ignore") as file_obj:
        reader_obj = csv.reader(file_obj)
        # skip heading
        heading = next(file_obj)

        targets = []
        for row in reader_obj:
            target = row[1]
            if not target in targets:
                targets.append(target)
        return targets


# print(sample_n_theme_from_csv(n=10))


# create profiles:
# will make bias of each category and loop back if n > number of profiles
# also flips bias of stance from 'FAVOR' to 'AGAINST' every time
# n: number of biased profiles to generate
def biased_profiles(n=1, n_per_cat=10, n_bias=15, n_nonbias=5, n_neutral=5):
    cats = all_targets()
    num_profile = 0
    profiles = []
    stace_fitler = ["FAVOR", "AGAINST"]
    flipper = True
    for cat in cats:
        if num_profile >= n:
            break
        profile = []
        for categ in cats:
            if categ == cat:
                bias_list = sample_n_theme_from_csv(
                    n=n_bias,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                    stance=stace_fitler[flipper],
                )
                bias_list = bias_list + sample_n_theme_from_csv(
                    n=n_nonbias,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                    stance=stace_fitler[not flipper],
                )
                bias_list = bias_list + sample_n_theme_from_csv(
                    n=n_neutral,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                    stance="NONE",
                )
                profile = profile + bias_list
            else:
                profile = profile + sample_n_theme_from_csv(
                    n=n_per_cat,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                )

        profiles.append(profile)
        num_profile = num_profile + 1
        flipper = not flipper
    write_profiles_to_file(profiles)
    return profiles


def write_profiles_to_file(profiles):
    with open(file="profiles.txt", mode="w") as file_obj:
        for idx, profile in enumerate(profiles):
            file_obj.writelines("~\n")
            file_obj.writelines("Profile number " + str(idx) + ":\n")
            for line in profile:
                file_obj.writelines(str(line) + "\n")


# profiles = biased_profiles(n=5)
