import csv
import bot
import nltk
from itertools import chain
from nltk.corpus import wordnet

# check if any words in message banned
def is_toxic(message) -> bool:
    is_banned = False

    with open('expanded_list.csv', 'r') as f1, open('expanded_list.csv', 'r') as f2:
        # words in given ban list
        file_reader = csv.reader(f1)

        # for each word, check against message
        for line in file_reader:
            # len for /n
            if len(line) > 0 and line[0] in message:
                # toxic message
                return True

        # words in expanded ban list
        file_reader2 = csv.reader(f1)
        for row in file_reader2:
            # len for /n at end of file
            if len(row) > 0 and row[0] in message:
                is_banned = True # may modify this later
                break
    
    return is_banned


# expand provided ban_list by including synonyms, etc
def expand_words():
    # create blank list for all synonyms
    lemmas = []

    with open('ban_list.csv', 'r') as f, open('expanded_list.csv', 'w') as newf:
        file_reader = csv.reader(f)
        write = csv.writer(newf, delimiter="\n")

        # for each line (banned word)
        for line in file_reader:
            # generate synonyms using nltk wordnet
            synonyms = wordnet.synsets(line[0])
            # parse and convert to a set
            lemmas += set(chain.from_iterable([word.lemma_names() for word in synonyms]))

        write.writerows([lemmas])


# use perspective api to calculate toxicity score
def api_toxicity(message) -> bool:
    # send request
    analyze_request = {
    'comment': { 'text': str(message)},
    'requestedAttributes': {'TOXICITY': {}} # can change attribute to SEVERE_TOXICITY etc
    }

    # retrieve response and parse for desired values
    response = bot.apiclient.comments().analyze(body=analyze_request).execute()
    toxicity_score = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

    # if above defined threshold, mark as toxis message
    if toxicity_score > float(bot.threshold):
        return True
    
    return False


def handle_response(message):
    p_message = message.lower()

    # check if message is toxic based on ban list and perspective api
    if is_toxic(message) or api_toxicity(message):
        return "User said something toxic"
    else:
        return None