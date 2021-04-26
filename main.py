import sys;
import os;
import configparser;
import time;
import shutil;
import re;
import getpass;

from PIL import Image;
# Init basic configuration parser
ConfigParser = configparser.ConfigParser();
Configuration = None;

# Application setup
os.system("title osu! ComboBurst Importer")
setupRequired = False;
skinDirectory = None;

if (not os.path.isfile("config.ini")):
    #Create default configuration
    ConfigParser["CONFIGURATION"] = {
        'PATH': "C:/Users/" + getpass.getuser() + "/AppData/Local/osu!/Skins"
    }

    ConfigParser["MODES"] = {
        "STANDARD": True,
        "MANIA": False,
        "TAIKO": False,
        "CTB": False
    }
    
    with open("config.ini", "w") as READING:
        ConfigParser.write(READING)

    setupRequired = True;
    print("Created configuration file.");

if (not os.path.isdir("combobursts")):
    setupRequired = True;
    os.mkdir("combobursts")
    print("Created \"combobursts\" folder.")

if (setupRequired):
    print( "\n" + ("=") * 16 + "\n");

# Check if anything is off with configuration file
if (os.path.isfile("config.ini")):
    ConfigParser.read("config.ini")
    if (not ConfigParser.has_section("CONFIGURATION")) or (not ConfigParser.has_option("CONFIGURATION", "PATH")):
        raise Exception("Path is not valid in `config.ini`. Please delete your config.ini file and try again.");
    if (not ConfigParser.has_section("MODES")):
        raise Exception("Modes header is not found in config.ini. Please delete your config.ini file and try again.");


if ("CONFIGURATION" in ConfigParser):
    print ("Skin folder location:", ConfigParser.get("CONFIGURATION", "PATH"));
    skinDirectory = ConfigParser.get("CONFIGURATION", "PATH");

# For Customization
def toggleMode(mode: str, value: bool):
    ConfigParser.set("CONFIGURATION", mode, value)
    return;


userToggles = [
    ["Standard", "STANDARD"],
    ["Mania", "MANIA"],
    ["Taiko", "TAIKO"],
    ["Catch The Beat", "CTB"]
]

userOptions = [
    "Create combobursts for all skins",
    "Create combobursts for a singular skin",
    "Create @2x variants for skins in ComboBurst folder\n",

    "Modes",
    "Exit"
]

# Define handlers for each option

def pasteSkin(Skin):
    atLeastOneModeToggled = False;

    for Toggle in enabledToggles:
        if Toggle[1] == "True":
            print("Inserting combo bursts for mode", Toggle[0][0].upper() + Toggle[0][1:].lower()); 
            print("=" * 32)
            print("Working on", Skin.name + "...")
            atLeastOneModeToggled = True;
            skinChoose(Skin.path + "/", Toggle[0].lower());
    
    return atLeastOneModeToggled;

def derive_new_burst_idx(SKIN_DIRECTORY: str, COMBOBURST_PREFIX: str, idx: int):
    result = SKIN_DIRECTORY + COMBOBURST_PREFIX + "-" + str(idx);
    return result

def sanitizeUserInput(Array):
    try:
        return max(int(input()) - 1, min(0, len(Array)-1));
    except ValueError:
        return False;
    

def singularSkinHandler():
    Skins = [[]];
    Page = 0;

    with os.scandir(skinDirectory) as skinFolder:
        for idx, Skin in enumerate(skinFolder):
            if idx != 0 and (idx % 6 is 0): # lol
                Page += 1;
            try:
                Skins[Page] = Skins[Page] or [];
            except IndexError:
                Skins.append([])

            Skins[Page].append(Skin);

    Page = 0; #Recycle page variable
    while True:
        os.system("cls");
        currentSkinPage = Skins[Page];
        for idx, Skin in enumerate(currentSkinPage):
            print(str(idx + 1) + ":", Skin.name);

        print("\n" + str(7) + ": Last Page | Next Page :", str(8))
        print("\t " + str(9) + ": Exit")



        try:
            
            try:
                userInput = int(input());

                if (userInput == 8):
                    try:
                        if (Skins[Page + 1]):
                            Page += 1;
                    except IndexError:
                        Page = Page;

                    print("Next Page.")
                if (userInput == 7):

                    try:
                        if (Skins[Page - 1]):
                            Page -= 1;
                    except IndexError:
                        Page = Page;

                    print("Last Page.")
                elif (userInput == 9):
                    break;

                pasteSkin(currentSkinPage[userInput])
                print("=" * 16)
                input("Done! Press ENTER to continue...");
                
            except ValueError:
                raise IndexError("Invalid value");
            
            break;
        except IndexError:
            continue;


        

        

        
def modeSelectionHandler():
    while True:
        os.system("cls");
        Toggles = [];
        for idx, Toggle in enumerate(userToggles):
            Enabled = ConfigParser.get("MODES", Toggle[1]) == "True";
            print(str(idx + 1) + ":", Toggle[0], "..", "Yes" if Enabled else "No");
            Toggles.append(Enabled)
        print("\n" + str(len(Toggles)+1) + ": Exit" )

        userInput = sanitizeUserInput(Toggles);
        if (userInput is False):
            continue;

        if (userInput == len(Toggles)):
            with open("config.ini", "w") as READING:
                ConfigParser.write(READING)

            return;
        elif ( (userInput) < len(Toggles) ) and (userToggles[userInput]):
            correspondingBoolean = userToggles[userInput][1]
            ConfigParser.set("MODES", correspondingBoolean, str(not Toggles[userInput]));


def skinChoose(skinDirectory, mode):
    Skins = [];
    ModeComboBurstIndices = {
        "standard": "comboburst",
        "mania": "comboburst-mania",
        "taiko": "taiko-flower-group",
        "ctb": "comboburst-fruits"
    }

    SKIN_DIRECTORY = skinDirectory + "/";

    if (not ModeComboBurstIndices[mode]):
        raise Exception("Invalid Mode: " + mode + ".")
    
    

    # Find all ComboBursts in the ComboBursts folder and cache them.
    cachedComboBursts = [];
    with os.scandir("combobursts") as comboBurstFolder:
        for comboBurstImage in comboBurstFolder:
            if (os.path.splitext(comboBurstImage.name)[1] != ".png"):
                os.system('cls')
                raise Exception("Image \"" + comboBurstImage.name + "\" is not a png file.");
            if not ("@2x" in comboBurstImage.name):
                cachedComboBursts.append([comboBurstImage.name, comboBurstImage.path])
            
    for idx, imageDirectory in enumerate(cachedComboBursts):
        IMAGE_NAME = os.path.splitext(imageDirectory[0])[0];
        COMBOBURST_PREFIX = ModeComboBurstIndices[mode];

        comboburstIndex = derive_new_burst_idx(SKIN_DIRECTORY, COMBOBURST_PREFIX, idx)

        while (os.path.exists(comboburstIndex + ".png") or os.path.exists(comboburstIndex + "@2x.png")):
            print(comboburstIndex, "already exists. Retrying...")
            idx += 1;
            comboburstIndex  = derive_new_burst_idx(SKIN_DIRECTORY, COMBOBURST_PREFIX, idx);
        
        shutil.copy2(imageDirectory[1], comboburstIndex + ".png")
        print("INAME:", IMAGE_NAME)
        # if there's a 2x variant then use place the 2x as well
        if (os.path.exists("combobursts/" + IMAGE_NAME + "@2x.png")):
            shutil.copy("combobursts/" + IMAGE_NAME + "@2x.png", comboburstIndex + "@2x.png")

while True:
    os.system("cls");
    for option_number, value in enumerate(userOptions):
        print( str(option_number + 1) + ": " + value  )
    userInput = input();
    
    enabledToggles = [
        ["STANDARD", ConfigParser.get("MODES", "STANDARD")],
        ["MANIA", ConfigParser.get("MODES", "MANIA")],
        ["TAIKO", ConfigParser.get("MODES", "TAIKO")],
        ["CTB", ConfigParser.get("MODES", "CTB")]
    ]

    if (userInput == "1"):
        with os.scandir(skinDirectory) as skinFolder:
            for Skin in skinFolder:
                os.system("cls");
                if (not pasteSkin(Skin)):
                    os.system("cls");
                    print("You don't have any modes toggled on! You might want to do that.")

        print("=" * 16)
        input("Done! Press ENTER to continue...");
    elif (userInput == "2"):
        singularSkinHandler();
    elif (userInput == "3"):
        with os.scandir("combobursts") as comboBurstFolder:
            for comboBurstImage in comboBurstFolder:
                fileName, fileExtension = os.path.splitext(comboBurstImage.name);
                if (fileExtension != ".png"):
                    os.system('cls')
                    raise Exception("Image \"" + comboBurstImage.name + "\" is not a png file.");
                
                if (not os.path.exists("combobursts/" + fileName + "@2x.png")) and not ("@2x" in fileName):
                    image = Image.open("combobursts/" + fileName + ".png")
                    image = image.resize( (image.size[0] * 2, image.size[1] * 2), Image.ANTIALIAS ).save("combobursts/" + fileName + "@2x.png")

        print("Finished creating @2x variants!");
        input("Press ENTER to continue...")
    elif (userInput == "4"):
        modeSelectionHandler();
    elif (userInput == "5"):
        break;
    else:
        print("Nope.")
    
