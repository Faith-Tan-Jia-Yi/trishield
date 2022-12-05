import csv
import bot


def is_toxic(message) -> bool:
    # Check if any of the words are found in the csv file
    is_banned = False

    with open('ban_list.csv', 'r') as f:
        file_reader = csv.reader(f)

        for line in file_reader:
            # banned words list
            if line[0] in message:
                is_banned = True
                break
    
    return is_banned


def handle_response(message) -> str:
    p_message = message.lower()

    # Check if toxic
    if is_toxic(message) or api_toxicity(message):
        return "User said something toxic"

    elif p_message == 'hello':
        return "I say hello back to you"

    elif p_message == '!help':
        return "`did you ask for my help?`"

    return "I don't understand you"


def api_toxicity(message) -> bool:
    # check using perspective api
    analyze_request = {
    'comment': { 'text': str(message)},
    'requestedAttributes': {'TOXICITY': {}} # can change attribute to SEVERE_TOXICITY etc
    }

    response = bot.apiclient.comments().analyze(body=analyze_request).execute()
    toxicity_score = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
    print(toxicity_score)

    if toxicity_score > float(bot.threshold):
        return True
    
    return False

