import csv
import pandas as pd
import random

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
) -> pd.DataFrame:
    start = 1
    start_found = False
    end = total_rows
    end_found = False
    if not theme == "all":
        with open(filename, encoding="utf8", errors="ignore") as file_obj:
            reader_obj = csv.reader(file_obj)
            # skip heading
            heading = next(file_obj)
            # print(list(reader_obj)[1][0])
            for idx, row in enumerate(reader_obj):
                if not start_found and row[1] == theme:
                    start = idx
                    start_found = True
                    print("start found: ", idx)
                if start_found and not end_found and not row[1] == theme:
                    end = idx
                    end_found = True
                    print("end found: ", idx)

    skip_rows = (
        list(range(1, start))
        + random.sample(range(start, end), (end - start) - n)
        + list(range(end, total_rows))
    )
    return pd.read_csv(
        filename,
        skiprows=skip_rows,
        encoding="utf8",
        encoding_errors="ignore",
        verbose=False,
    )


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


print(sample_n_theme_from_csv(n=10))
