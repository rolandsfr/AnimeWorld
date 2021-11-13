import json
import os
import requests
import random

# Defining utility class to later validate values and types of input data
class Types():
    def _anyParser(self, val):
        return len(val) != 0

    def __init__(self):
        self.parsers = [{"any": self._anyParser}]

        
    def validate(self, value, type):
        # First of all validate the any type (non empty)
        nonEmpty = self._anyParser(value)
        if(nonEmpty == False):
            raise ValueError("Please, enter a value")        

        for parser in self.parsers:
            for key in parser.keys():
                if key == type:
                    isValidOrException = parser[key](value)
                    if(isValidOrException != True):
                        raise ValueError(isValidOrException)

    def add(self, type, parserFunc):
        # parser function returns boolean whether or not the value was parsed successfully
        self.parsers.append({type: parserFunc})

def ynParser(val):
    if(val == "y" or val == "n" or val == "yes" or val == "no"):
        return True
    else:
        return ValueError(f"Value {val} is not assignable to type yes/no/y/n")

def animeParser(val):
    ALLOWED = [
        "naruto",
        "one piece",
        "pokemon",
        "attack on titan",
    ]

    if(val.lower() in ALLOWED):
        return True
    else:
        serialized = " / ".join(ALLOWED)
        return ValueError(f"Anime {val} is not in list of provided animes. Please select one from the below listed:\n{serialized}")

# initializing utility types
types = Types()
types.add("yn", ynParser)
types.add("anime", animeParser)

# Looping on the incorrect values
def inputWithValidation(query, type = "any"):
    value = ""
    loop = True    

    while(loop):
        value = input(query)
        try:
            types.validate(value, type)
            loop = False;            
        except Exception as e:
            print(str(e))

    return value


def getRandomFact(anime):
    print("\nFetching an external resource...")
    response = requests.get(f"https://anime-facts-rest-api.herokuapp.com/api/v1/{anime}")
    data = response.json()["data"]
    randomId = random.randint(1, len(data))
    funFact = ""

    for fact in data:
        if fact["fact_id"] == randomId:
            funFact = fact["fact"]

    return funFact

def downloadAnime(fileName):
    print("\nDownloading anime image...")
    response = requests.get("https://api.waifu.pics/sfw/poke")
    url = response.json()["url"]
    imageResponse = requests.get(url)

    # create a file and subdirectory
    if(os.path.exists("assets") != True):
        os.mkdir("assets")
    
    file = open("assets/" + fileName, "wb")
    file.write(imageResponse.content)
    file.close()

    print("Congrats! Your anime is waiting for you in the assets/anime.gif file!\nEnjoy and thanks for using AnimeWorld :)\n")

def initApp():
    completeName = "user.json"
    animeFileName = "anime.gif"

    def initializeUser():
        print("Hello, Welcome to AnimeWorld!\nWe first need to gather some information before we can start.")
        name = inputWithValidation("Whats your name? ")
        fav = inputWithValidation("What is your favorite anime? ", "anime")
        additional = inputWithValidation("Do you want to receive a random anime image on startup? yes/no/y/n ", "yn")

        config = {
            "name": name,
            "favorite": fav,
            "sendImage": True if additional == "yes" or additional == "y" else False
        }

        with open(completeName, "w+") as f:
            json.dump(config, f)

        return config            

    def startWork(config):
        # greet the user
        name = config["name"]
        favorite = config["favorite"].replace(" ", "_")
        print(f"Welcome back, {name}!")

        # fetch facts about the favorite anime
        fact = getRandomFact(favorite).replace(".", "")
        print(f"\n\nHere's a random fact about your favorite anime `{favorite}`!\n - Did you know that {fact}?\n")

        # download an anime fig
        downloadAnime(animeFileName)
         
    try:
        initialConfig = open(completeName, "r")
        parsedConfig = json.loads(initialConfig.read())
        startWork(parsedConfig)
    except Exception as e:
        config = initializeUser() 
        startWork(config)        

initApp()