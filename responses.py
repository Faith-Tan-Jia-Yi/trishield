import csv


def is_toxic(message) -> bool:
    # Check if any of the words are found in the csv file
    is_banned = False

    with open('ban_list.csv', 'r') as f:
        file_reader = csv.reader(f)

        for line in file_reader:
            if line[0] in message:
                is_banned = True
                break

    # Check using our fake Perspective API
    is_api_toxic = False
    # todo: random number generator to find out if its toxic or just use the real api

    return is_banned or is_api_toxic


def handle_response(message):
    p_message = message.lower()

    # Check if toxic
    if is_toxic(p_message):
        return "Please do consider changing your message"
    else:
        return None

    

