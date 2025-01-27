from ast import literal_eval
import requests
import json
from datetime import datetime
import re
from configuration import *

def set_postcode_screen():
    print("\n")
    print("    ----- POSTCODE PAGE -----\n")
    postcode = input("Write your current uk postcode (without spaces): ")
    res = requests.get(f"{api_protocol}{api_host}:{api_port}/postcode_check/{postcode}")
    if res.status_code != 200:
        print("Invalid postcode. Type any key and try again: ")
        input()
        return set_postcode_screen()
    return postcode

def main_menu_screen(postcode):
    # print(postcode)
    print("\n")
    print("""
    ----- MAIN MENU PAGE -----

    1. Search for available rooms
    2. Cancel a room application
    3. View history of room applications 
    4. Change my postcode    
    """)

    chosen_option = input("Select option: ")
    # print(type(chosen_option))
    if chosen_option == "1":
        available_rooms_screen(postcode)
    elif chosen_option == "2":
        cancel_applications_screen(postcode)
    elif chosen_option == "3":
        applicaiton_history_screen(postcode)
    elif chosen_option == "4":
        new_postcode = set_postcode_screen()
        print("Successfully changed your passcode!. Type any key to continue: ")
        input()
        main_menu_screen(new_postcode)
    else:
        print("Invalid option. Type any key and try again: ")
        input()
        main_menu_screen(postcode)

def available_rooms_screen(postcode):
    res = requests.get(f"{api_protocol}{api_host}:{api_port}/rooms/{postcode}")
    rooms = json.loads(res.content)
    i = 0
    print("\n")
    print("    ----- ROOMS FOR SALE PAGE -----\n")
    for i in range(len(rooms)):
        print(f"    {i+1}. {rooms[i][1]}, {rooms[i][2]}, {rooms[i][4]}, distance: {rooms[i][14]}, price: {rooms[i][11]}")
    print(f"    {i+2}. Go back\n")

    chosen_option = input("Select option: ")
    try:
        chosen_option = int(chosen_option)
    except ValueError:
        print("Invalid input. Type any key and try again: ")
        input()
        available_rooms_screen(postcode)


    if chosen_option <= len(rooms):
        room_screen(postcode, rooms[chosen_option-1][0])
    elif chosen_option == i+2:
        main_menu_screen(postcode)

def room_screen(postcode, id):
    res = requests.get(f"{api_protocol}{api_host}:{api_port}/room/{id},{postcode}")
    data = json.loads(res.content)
    room = re.sub(r"Decimal\('([\d.]+)'\)", r'\1', data["room"])
    room = re.sub(r"datetime\.date\((\d+), (\d+), (\d+)\)", r'"\1-\2-\3"', room)
    room = room.replace("'", '"')
    room = json.loads(room)

    weather = data["weather24hr"]
    pending_application = data["pending_application"]

    pending_application_text = None
    if pending_application == None:
        pending_application_text = "Apply for this room"
    else:
        date_obj = datetime.strptime(pending_application[5], "%Y-%m-%dT%H:%M:%S")
        date_created_formatted = date_obj.strftime("%H:%M %d-%B-%Y")

        pending_application_text = f"Cancel ongoing application for this room (submitted on {date_created_formatted})"

    furnished = "No"
    if room[5] == 1:
        furnished = "Yes"
    
    live_in_landlord = "No"
    if room[7] == 1:
        live_in_landlord = "Yes"

    bills_included = "No"
    if room[9] == 1:
        bills_included = "Yes"

    bathroom_shared = "No"
    if room[10] == 1:
       bathroom_shared = "Yes" 

    percipitation = ""
    for p in literal_eval(weather["percipitation"]):
        percipitation += f" {p},"
    percipitation = percipitation[:-1]

    print(f"""
    ----- ROOM PAGE -----

    Room info:

    {room[1]}

    Address:
    {room[2]}, {room[3]}, {room[4]} ({data["distance"]} meters away from you)

    Number of crimes last month in the area: {data["num_of_crimes_past_month"]}

    Information:

    Furnished - {furnished}
    Live-In landlord - {live_in_landlord}
    Bills included - {bills_included}
    Shared bathroom - {bathroom_shared}

    Weather in {room[2]} today: 
    
    min. temperature: {weather["temp_min"]}
    max. temperature: {weather["temp_max"]}
    percipitation: {percipitation}


    1. {pending_application_text}
    2. Go back
    """)

    selected_option = input("Select option: ")
    if selected_option == "1":
        if pending_application != None:
            res = cancel_application(pending_application[0])
            if res.status_code == 200:
                print("Success. Type any key to continue: ")
            else:
                print("Failed to cancel application. Type any key and try again later: ")
            input()
            room_screen(postcode, id)

        else:
            create_application_screen(postcode, room[0], room[1])
    elif selected_option == "2":
        available_rooms_screen(postcode)
    else:
        print("Invalid option. Type any key and try again: ")
        input()
        room_screen(postcode, id)

            
def create_application_screen(postcode, room_id, room_name):
    print("\n")
    print("    ----- NEW APPLICATION PAGE -----\n")
    months = input("For how many months would you like to rent this room (write a number): ")
    try:
        int(months)
    except ValueError:
        print("Invalid input. Type any key and try again: ")
        input()
        create_application_screen(postcode, room_id, room_name)

    res = requests.get(f"{api_protocol}{api_host}:{api_port}/room/apply/{room_id},{months},{room_name}")
    
    if res.status_code == 200:
        print("Success. Type any key to continue: ")
    else:
        print("Failed to submit application. Type any key and try again later: ")
    input()
    room_screen(postcode, room_id)


def cancel_application(application_id):
    # print(application_id)
    
    return requests.get(f"{api_protocol}{api_host}:{api_port}/applications/cancel/{application_id}")


def cancel_applications_screen(postcode):
    res = requests.get(f"{api_protocol}{api_host}:{api_port}/applications/status/pending")
    data = json.loads(res.content)

    print("\n    ----- CANCEL APPLICATION PAGE -----\n")
    print("Choose the application to cancel.\n")

    if len(data) != 0:
        i = 0
        for i in range(len(data)):
            date_obj = datetime.strptime(data[i][5], "%Y-%m-%dT%H:%M:%S")
            date_created_formatted = date_obj.strftime("%H:%M %d-%B-%Y")
            print(f"{i+1}. {data[i][4]}, {data[i][1]}, {date_created_formatted}")
        print(f"{i+2}. Go back")

        chosen_option = input("Select option: ")

        try:
            chosen_option = int(chosen_option)
        except ValueError:
            print("Invalid input. Type any key and try again: ")
            input()
            cancel_applications_screen(postcode)

        if chosen_option <= len(data):
            # print("inside")
            res = cancel_application(data[chosen_option-1][0])
            if res.status_code == 200:
                print("Success. Type any key to continue: ")
            else:
                print("Failed to cancel application. Type any key and try again later: ")
            input()
            cancel_applications_screen(postcode)

        elif chosen_option == i+2:
            main_menu_screen(postcode)
    else:
        print("You don't have any pending applications.\n\nType any key to go back: ")
        input()
        main_menu_screen(postcode)


def applicaiton_history_screen(postcode):
    res = requests.get(f"{api_protocol}{api_host}:{api_port}/applications")
    data = json.loads(res.content)

    print("\n    ----- APPLICATION HISTORY PAGE -----\n")
    print("    Your history of applications and their results:\n")

    for application in data:
        date_obj = datetime.strptime(application[5], "%Y-%m-%dT%H:%M:%S")
        date_created_formatted = date_obj.strftime("%H:%M %d-%B-%Y")
        print(f"    {application[4]}, {application[1]}, months: {2}, date created: {date_created_formatted}")

    print("\nType any key to go back: ")
    input()
    main_menu_screen(postcode)


if __name__ == "__main__":
    postcode = set_postcode_screen()
    main_menu_screen(postcode)
