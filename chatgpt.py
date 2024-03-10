from openai import OpenAI
import loadData
from tqdm import tqdm
import os

# This code requires an openai api key to run
# To use your secret key create a .env file and add the following line:
# OPENAI_API_KEY= Your Secret Key Here
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Class that holds all modules for bias detection
class profile:
    def __init__(
        self, tweets, categories=[], new_cat=False, true_targets=[], true_stances=[]
    ):
        self.tweets = tweets
        self.categories = categories
        self.new_cat = new_cat
        self.log = []
        self.choices = ["'in-favor'", "'against'", "'neutral-or-unclear'"]
        self.true_profile = {}
        self.profile = {}
        self.true_targets = true_targets
        self.true_stances = true_stances
        self.bias = {"in-favor": [], "against": []}
        self.true_bias = {"in-favor": [], "against": []}
        self.__init_profile__()

    # prompt GPT to detect the stance of a tweet
    def stance_detection(self, tweet, category):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "What is the stance of the tweet below with respect to '"
                    + category
                    + "'?  If we can infer from the tweet that the tweeter supports '"
                    + category
                    + "', please label it as 'FAVOR'. If we can infer from the tweet that the tweeter is against '"
                    + category
                    + "', please label is as 'AGAINST'. If we can infer from the tweet that the tweeter has a neutral stance towards '"
                    + category
                    + "', please label it as 'NONE'. If there is no clue in the tweet to reveal the stance of the tweeter towards '"
                    + category
                    + "', please also label is as 'NONE'. Please use exactly one word from the following 3 categories to label it: 'FAVOR', 'AGAINST', 'NONE'. Here is the tweet. '"
                    + tweet
                    + "'. The stance of the tweet is:",
                },
            ],
        )
        answer = completion.choices[0].message.content
        return answer

    # prompt  GPT to detect in which category the tweet belongs in
    def inCategories(self, tweet):
        unknown_allowed = ""
        # release this prompt if want to allow for the system to create new categories
        if self.new_cat:
            unknown_allowed = " if the tweet does not fit in any of the above categories answer with 'Unknown'"
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "In which debate category does the tweet below belong in? Following categories: "
                    + ", ".join(self.categories)
                    + ". You must answer only with the full name of one of the categories above."
                    + unknown_allowed
                    + "  Here is the tweet: '"
                    + tweet
                    + "' The category of the tweet is: ",
                },
            ],
        )
        answer = completion.choices[0].message.content
        return answer

    # Generate the name for a new  category
    def createCategory(self, tweet):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": "Create a descriptive category name for the debate that the tweet below is talking about. Include the relevant important terms. Answer only with the category name."
                    + "Use the same format as these examples: Pro marijuana legalisation, Against total freedom of expression, Against Vegan movement, Pro European Union, Against Government funded propaganda"
                    + " Make the new name is distinct from the following categories: "
                    + ", ".join(self.categories)
                    + "Here is the tweet: '"
                    + tweet
                    + "' The category of the tweet is: ",
                },
                # suggest a new name for the category that specifically describes in depth the debate topic in the tweet
            ],
        )
        answer = completion.choices[0].message.content
        print("creating new category: ", answer)
        return answer

    # Add predefined cateogories to profile
    def __init_profile__(self):
        for cat in self.categories:
            self.profile[cat] = [0, 0, 0]
            self.true_profile[cat] = [0, 0, 0]

    # update profile with the answer of GPT
    def update_profile(self, category, ans):
        if ans == "FAVOR":
            self.profile[category][0] = self.profile[category][0] + 1
        if ans == "AGAINST":
            self.profile[category][1] = self.profile[category][1] + 1
        else:
            self.profile[category][2] = self.profile[category][2] + 1

    # Write log history to file
    def write_log_to_file(self, fileName="log.txt"):
        with open(file=fileName, mode="w") as file_obj:
            for lines in self.log:
                file_obj.writelines("-------------------------------------\n")
                file_obj.writelines(str(lines) + "\n")

    # calculate the acuracy of the model on detecting the correct category for tweets
    def accuracy_targets(self):
        if not self.true_targets == []:
            correct = 0
            for idx, label in enumerate(self.true_targets):
                if label == self.log[idx][1]:
                    correct = correct + 1
            average = correct / len(self.true_targets)
            return average
        else:
            print("need targets")

    # calculate the acuracy of the model on detecting the correct stancea for tweets
    def accuracy_stances(self):
        if not self.true_stances == []:
            correct = 0
            for idx, label in enumerate(self.true_stances):
                if label == self.log[idx][3]:
                    correct = correct + 1
            average = correct / len(self.true_stances)
            return average
        else:
            print("need stances")

    # Go through profile and detected stances and categories
    # aggragate to see if one category manifest a lot of bias towards one stance
    def find_bias(self):
        for cat in self.categories:

            num_favor = self.profile[cat][0]
            num_against = self.profile[cat][1]
            if num_favor == 0 and num_against == 0:
                print("bias: no tweets in that category")
                return self.bias
            elif num_favor == 0:
                print("bias: only tweets against")
                self.bias["against"].append(cat)
                return self.bias
            elif num_against == 0:
                print("bias: only tweets in favor")
                self.bias["in-favor"].append(cat)
                return self.bias
            ratio = num_favor / num_against
            if ratio >= 2:
                print(
                    "Careful, you might have a bias for 'in favor' of category: ",
                    cat,
                    ". The calulated ratio was: ",
                    ratio,
                )
                self.bias["in-favor"].append(cat)

            if ratio <= 0.5:
                print(
                    "Careful, you might have a bias for 'agaisnt' of category: ",
                    cat,
                    ". The calulated ratio was: ",
                    ratio,
                )
                self.bias["against"].append(cat)

    # Same as find_bias() but uses true stances
    # this gives the true accuracy based on the labels of the dataset
    def find_true_bias(self):
        for idx, (category, stance) in enumerate(
            zip(self.true_targets, self.true_stances)
        ):
            if stance == "FAVOR":
                self.true_profile[category][0] = self.true_profile[category][0] + 1
            if stance == "AGAINST":
                self.true_profile[category][1] = self.true_profile[category][1] + 1
            else:
                self.true_profile[category][2] = self.true_profile[category][2] + 1

        for cat in self.categories:
            num_favor = self.true_profile[cat][0]
            num_against = self.true_profile[cat][1]
            if num_favor == 0 and num_against == 0:
                print("true bias: no tweets in that category")
                return self.bias
            elif num_favor == 0:
                print("true bias: only tweets against")
                self.bias["against"].append(cat)
                return self.bias
            elif num_against == 0:
                print("true bias: only tweets in favor")
                self.bias["in-favor"].append(cat)
                return self.bias
            ratio = num_favor / num_against
            if ratio >= 2:
                print(
                    "True Profile: ",
                    cat,
                    ". The calulated ratio was: ",
                    ratio,
                )
                self.true_bias["in-favor"].append(cat)

            elif ratio <= 0.5:
                print(
                    "True Profile: ",
                    cat,
                    ". The calulated ratio was: ",
                    ratio,
                )
                self.true_bias["against"].append(cat)
            return self.true_bias

    # run the model pipeline on all the given tweets
    def run(self):
        for idx, tweet in tqdm(enumerate(self.tweets)):
            category = self.inCategories(tweet)
            #  If GPT decides tweet does not fit one of the given categories, create a new one and add it to the list of possible categories
            if self.categories == [] or category == "Unknown":
                category = self.createCategory(tweet)
                self.categories.append(category)
                self.profile[category] = [0, 0, 0]
            ans = self.stance_detection(tweet, category)
            self.update_profile(category, ans)
            self.log.append(
                [
                    tweet,
                    category,
                    self.true_targets[idx],
                    ans,
                    self.true_stances[idx],
                    self.profile[category],
                ]
            )
        self.write_log_to_file()
        print("Accuracy on categories: ", self.accuracy_targets() * 100, "%")
        print("Accuracy on stances: ", self.accuracy_stances() * 100, "%")
        self.find_bias()
        self.find_true_bias()
        return self.bias, self.true_bias, self.profile, self.true_profile


# load in tweets and labels
sample = loadData.sample_n_theme_from_csv(n=10)
targets_label = loadData.all_targets()
tweets = [row[0] for row in sample]
true_targets = [row[1] for row in sample]
true_stances = [row[2] for row in sample]
# print("tweets: ", tweets)

profile = profile(
    tweets=tweets,
    categories=targets_label,
    new_cat=False,
    true_targets=true_targets,
    true_stances=true_stances,
)
res = profile.run()
print(res)

# profile = profile(
#     tweets=tweets,
#     new_cat=True,
#     true_targets=true_targets,
#     true_stances=true_stances,
# )
# res = profile.run()
# print(res)

# stance detection with true categories:
# correct = 0
# for idx, tweet in enumerate(tweets):
#     stance = profile.stance_detection(tweet, true_targets[idx])
#     if stance == true_stances[idx]:
#         correct = correct + 1
# average = correct / len(true_stances)
# print("stance detection with true categories: ", average * 100, "%")

## ---- Test bias detection in profiles ----

# profiles = loadData.biased_profiles(
#     n=1, n_per_cat=10, n_bias=15, n_nonbias=5, n_neutral=5
# )
# for prof in profiles:
#     targets_label = loadData.all_targets()
#     print(targets_label)
#     tweets = [row[0] for row in prof]
#     true_targets = [row[1] for row in prof]
#     true_stances = [row[2] for row in prof]

#     profile_instance = profile(
#         tweets=tweets,
#         categories=targets_label,
#         new_cat=False,
#         true_targets=true_targets,
#         true_stances=true_stances,
#     )
#     bias, true_bias, prof, true_prof = profile_instance.run()
#     print("------------------")
#     print("Bias: ", bias)
#     print("True Bias: ", bias)
#     print("Profile: ", prof)
#     print("True Profile: ", true_prof)
#     print("------------------")
