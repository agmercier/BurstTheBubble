import csv
import pandas as pd
import random
import numpy as np

# 2915 training posts
# 1957 testing posts


# sample n tweets from filename
# total rows is the total amount of tweets in filename
def sample_n_from_csv(
    filename: str, n: int = 100, total_rows: int = 2915
) -> pd.DataFrame:
    # read_csv only takes indecies to skip for some reason not to sample from
    # So instead we are generating total_rows - n random indecies to skip and sampling the rest.
    skip_rows = random.sample(range(1, total_rows + 1), total_rows - n)
    return pd.read_csv(
        filename, skiprows=skip_rows, encoding="utf8", encoding_errors="ignore"
    )


# sample n tweets from filename
# total rows is the total amount of tweets in filename
# Same as above method but now includes a theme and stance filter.
# Sample only from tweets with the desired stance/theme
# Passing "all" removes the filter
def sample_n_theme_from_csv(
    filename: str = "StanceDataset\\train.csv",
    n: int = 100,
    total_rows: int = 2915,
    theme: str = "all",
    stance: str = "all",
) -> pd.DataFrame:
    skip = []
    all = []
    with open(filename, encoding="utf8", errors="ignore") as file_obj:
        reader_obj = csv.reader(file_obj)
        # skip heading (name of columns)
        heading = next(file_obj)
        # for every row
        for idx, row in enumerate(reader_obj):
            # append row
            all.append(row)
            # add to skipped rows if not it filter
            if (not theme == "all") and (not theme == row[1]):
                skip.append(idx)
            if (not stance == "all") and (not stance == row[2]):
                skip.append(idx)
    # remove skipped rows from available indecies
    possible = list(set(range(1, total_rows)).difference(skip))
    # sample n from filtered list
    sample_rows = random.sample(possible, n)
    # return sampled rows
    return [x for iter, x in enumerate(all) if iter in sample_rows]


# def data_from_csv(filename: str) -> pd.DataFrame:
#     return pd.read_csv(filename, encoding="utf8", encoding_errors="ignore")


# all_data = data_from_csv("StanceDataset\\train.csv")
# print([all_data["Target"] == "Hillary Clinton"])


# find all target names in filename
def all_targets(filename: str = "StanceDataset\\test.csv"):
    with open(filename, encoding="utf8", errors="ignore") as file_obj:
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
# For each new profile will make bias a new category and loop back if n > number of profiles
# also flips bias of stance from 'FAVOR' to 'AGAINST' every time
# n: number of biased profiles to generate
def biased_profiles(n=1, n_per_cat=10, n_bias=10, n_nonbias=2, n_neutral=5):
    # all category names in file
    cats = all_targets()
    # instantiate number of profiles created
    num_profile = 0
    # instantiate list of created profiles
    profiles = []
    # flip between in favor and against stances when creating new profile.
    stance_fitler = ["FAVOR", "AGAINST"]
    flipper = False
    # loop through to create n profiles
    while num_profile < n:
        # index of category which will be made bias in the profile
        bias_cat = np.mod(num_profile, len(cats))
        profile = []
        # add tweets to profile from that category with a skewed ratio
        for categ in cats:
            if categ == cats[bias_cat]:
                bias_list = sample_n_theme_from_csv(
                    n=n_bias,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                    stance=stance_fitler[flipper],
                )
                bias_list = bias_list + sample_n_theme_from_csv(
                    n=n_nonbias,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                    stance=stance_fitler[not flipper],
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
                # randomly sample tweets for other categories
                profile = profile + sample_n_theme_from_csv(
                    n=n_per_cat,
                    filename="StanceDataset\\test.csv",
                    total_rows=1957,
                    theme=categ,
                )
        # add profile to list
        profiles.append(profile)
        num_profile = num_profile + 1
        # flip stance for next profile
        flipper = not flipper
    write_profiles_to_file(profiles)
    return profiles


# write a profile to file
def write_profiles_to_file(profiles):
    with open(file="profiles.txt", mode="w") as file_obj:
        for idx, profile in enumerate(profiles):
            file_obj.writelines("~\n")
            file_obj.writelines("Profile number " + str(idx) + ":\n")
            for line in profile:
                file_obj.writelines(str(line) + "\n")


# profiles = biased_profiles(n=5)
# print(profiles)
