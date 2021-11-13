import json
import os
import requests
import random


# Defining utility class to later validate values and types of input data
class Types:
    def _any_parser(self, val):
        return len(val) != 0

    def __init__(self):
        self.parsers = [{"any": self._any_parser}]

    def validate(self, value, type):
        # First of all validate the any type (non empty)
        non_empty = self._any_parser(value)
        if non_empty == False:
            raise ValueError("Please, enter a value")

        for parser in self.parsers:
            for key in parser.keys():
                if key == type:
                    is_valid_or_exception = parser[key](value)
                    if is_valid_or_exception != True:
                        raise ValueError(is_valid_or_exception)

    def add(self, type, parser_func):
        # parser function returns boolean whether or not the value was parsed successfully
        self.parsers.append({type: parser_func})


def yn_parser(val):
    if val == "y" or val == "n" or val == "yes" or val == "no":
        return True
    else:
        return ValueError(f"Value {val} is not assignable to type yes/no/y/n")


def anime_parser(val):
    ALLOWED = [
        "naruto",
        "one piece",
        "pokemon",
        "attack on titan",
    ]

    if val.lower() in ALLOWED:
        return True
    else:
        serialized = " / ".join(ALLOWED)
        return ValueError(
            f"Anime {val} is not in list of provided animes. Please select one from the below listed:\n{serialized}"
        )


# initializing utility types
types = Types()
types.add("yn", yn_parser)
types.add("anime", anime_parser)


# Looping on the incorrect values
def input_with_validation(query, type="any"):
    value = ""
    loop = True

    while loop:
        value = input(query)
        try:
            types.validate(value, type)
            loop = False
        except Exception as e:
            print(str(e))

    return value


def get_random_fact(anime):
    print("\nFetching an external resource...")
    response = requests.get(
        f"https://anime-facts-rest-api.herokuapp.com/api/v1/{anime}"
    )
    data = response.json()["data"]
    random_id = random.randint(1, len(data))
    fun_fact = ""

    for fact in data:
        if fact["fact_id"] == random_id:
            fun_fact = fact["fact"]

    return fun_fact


def download_anime(fileName):
    print("\nDownloading anime image...")
    response = requests.get("https://api.waifu.pics/sfw/poke")
    url = response.json()["url"]
    image_response = requests.get(url)

    # create a file and subdirectory
    if os.path.exists("assets") != True:
        os.mkdir("assets")

    file = open("assets/" + fileName, "wb")
    file.write(image_response.content)
    file.close()

    print(
        "Congrats! Your anime is waiting for you in the assets/anime.gif file!\nEnjoy and thanks for using AnimeWorld :)\n"
    )


def init_app():
    complete_name = "user.json"
    anime_file_name = "anime.gif"

    def initialize_user():
        print(
            "Hello, Welcome to AnimeWorld!\nWe first need to gather some information before we can start."
        )
        name = input_with_validation("Whats your name? ")
        fav = input_with_validation("What is your favorite anime? ", "anime")
        additional = input_with_validation(
            "Do you want to receive a random anime image on startup? yes/no/y/n ", "yn"
        )

        config = {
            "name": name,
            "favorite": fav,
            "sendImage": True if additional == "yes" or additional == "y" else False,
        }

        with open(complete_name, "w+") as f:
            json.dump(config, f)

        return config

    def start_work(config):
        # greet the user
        name = config["name"]
        favorite = config["favorite"].replace(" ", "_")
        print(f"Welcome back, {name}!")

        # fetch facts about the favorite anime
        fact = get_random_fact(favorite).replace(".", "")
        print(
            f"\n\nHere's a random fact about your favorite anime `{favorite}`!\n - Did you know that {fact}?\n"
        )

        # download an anime fig
        download_anime(anime_file_name)

    try:
        initial_config = open(complete_name, "r")
        parsed_config = json.loads(initial_config.read())
        start_work(parsed_config)
    except Exception as e:
        config = initialize_user()
        start_work(config)


init_app()
