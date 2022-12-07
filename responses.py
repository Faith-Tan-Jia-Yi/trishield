import os
from dotenv import load_dotenv
from googleapiclient import discovery
import csv
import nltk
from itertools import chain
from nltk.corpus import wordnet
import difflib

# initialize according to .env file
def init_env():
    load_dotenv()

    # defining toggled checks defined in .env
    global toggle_tox
    toggle_tox = os.getenv('PERSPECTIVE')

    global toggle_censor
    toggle_censor = os.getenv('CENSORED')

    # initializing thresholds from .env file
    global tox_threshold
    tox_threshold = os.getenv('TOXICITY_THRESHOLD')

    global censor_threshold
    censor_threshold = os.getenv('CENSOR_THRESHOLD')

    if (toggle_tox == "1"):
        # API Key, defined in .env file
        TOKEN = os.getenv('PERSPECTIVE_TOKEN')

        # setting up perspective api client
        PERSPECTIVE = os.getenv('PERSPECTIVE_TOKEN')
        global apiclient
        apiclient = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=TOKEN,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        )


    # expand list of banned words to include synonyms
    expand_words()



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

# check if user misspells or censors banned word based off provided file
def spell_check(message) -> bool:
    with open('ban_list.csv', 'r') as f:
        file_reader = csv.reader(f)

        for word in file_reader:
            # find closest match for banned word in message
            closest = difflib.get_close_matches(word[0], message.split(), 1)
            # if no match found
            if len(closest) == 0:
                closest = [""]
            try:
                # similarity ratio between match and banned word
                ratio = difflib.SequenceMatcher(None, closest[0], word[0]).ratio()
            except:
                ratio = 0
            # above threshold, toxic message
            if ratio >= float(censor_threshold):
                print("censor ratio: " + str(ratio))
                return True


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

    # bug: some words not recognized as english, temp fix via try-except
    try:
        response = apiclient.comments().analyze(body=analyze_request).execute()
        toxicity_score = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
    except:
        toxicity_score = 0

    # if above defined threshold, mark as toxis message
    if toxicity_score >= float(tox_threshold):
        print("toxicity score: " + str(toxicity_score))
        return True
    
    return False

# check user message based on settings
def handle_response(message):
    p_message = message.lower()
    # check if message is toxic based on ban list
    if is_toxic(message):
        print("ban word triggered")
        return "User said something toxic"
    # if perspective api toggled, check message toxicity
    if (toggle_tox == "1" and api_toxicity(message)):
        print("tox triggered")
        return "User said something toxic"
    # if censor check toggeled, check banned words with censor/spell check
    if (toggle_censor == "1" and spell_check(message)):
        print("censor triggered")
        return "User said something toxic"
    else:
        return None