from openai import OpenAI
import loadData

client = OpenAI(api_key="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")


# tweets = [
#     "It's so brilliant that #lovewins - now extend the equality to women's rights #abortionrights.",
#     "Abortion is murder, don't kill you child",
#     "AI steals all art. Should not be allowed to train without paying the artists",
#     "AI does not need to pay artists, it is just taking inspiration from their art, nothing else",
#     "Climate change is real and coming for us all",
#     "Climate change is not real, its is just a hoax",
# ]


class profile:
    def __init__(
        self, tweets, categories=[], new_cat=False, true_targets=[], true_stances=[]
    ):
        self.tweets = tweets
        self.categories = categories
        self.new_cat = new_cat
        self.log = []
        self.choices = ["'in-favor'", "'against'", "'neutral-or-unclear'"]
        self.profile = {}
        self.true_targets = true_targets
        self.true_stances = true_stances
        self.__init_profile__()

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

    def inCategories(self, tweet):
        unknown_allowed = ""
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
                    + ". You must answer only with the full name of the category."
                    + unknown_allowed
                    + "  Here is the tweet: '"
                    + tweet
                    + "' The category of the tweet is: ",
                },
            ],
        )
        answer = completion.choices[0].message.content
        return answer

    def createCategory(self, tweet):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": "Create a highly descriptive category name for the debate the tweet below is talking about. Include the relevant important terms. Answer only with the category name."
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

    def __init_profile__(self):
        for cat in self.categories:
            self.profile[cat] = 0

    def write_log_to_file(self, fileName="log.txt"):
        with open(file=fileName, mode="w") as file_obj:
            for lines in self.log:
                file_obj.writelines("-------------------------------------\n")
                file_obj.writelines(str(lines) + "\n")

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

    def run(self):
        for idx, tweet in enumerate(self.tweets):
            category = self.inCategories(tweet)
            if category == "Unknown":
                category = self.createCategory(tweet)
                self.categories.append(category)
                self.profile[category] = 0
            ans = self.stance_detection(tweet, category)
            if ans == "FAVOR":
                self.profile[category] = self.profile[category] + 1
            if ans == "AGAINST":
                self.profile[category] = self.profile[category] - 1
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
        return self.profile


sample = loadData.sample_n_theme_from_csv(n=30).to_numpy()
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
