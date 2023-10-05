# Import your dependencies
import os
import datetime
from nylas import APIClient
from dotenv import load_dotenv

# Load your env variables
load_dotenv()

# Initialize your Nylas API client
nylas = APIClient(
    os.environ.get("CLIENT_ID"),
    os.environ.get("CLIENT_SECRET"),
    os.environ.get("ACCESS_TOKEN"),
)

# Retun all calendars for a user account
calendars = nylas.calendars.all()
# Get the ID of the "Prospect Meetings" calendar
calendar_id = [ calendar['id'] for calendar in calendars if '<YOUR_CALENDAR_NAME>' in calendar['name'] ][0]

today = datetime.date.today()

# Get Monday's datetime and convert it to a unix timestamp
monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
monday_unix = monday.strftime("%s")

# Get Friday's datetime and convert it to a unix timestamp
friday = monday + datetime.timedelta(days=5)
friday_unix = friday.strftime("%s")

# Find all events on the Prospect Meetings calendar between this Monday and Friday
events = nylas.events.where(
  calendar_id=calendar_id, 
  starts_after=monday_unix, 
  ends_before=friday_unix
)

internal_employees = []
external_prospects = []
this_meeting = {}
for event in events:
    for participant in event["participants"]:
        # If our company domain is in the participant's email, they're our employee
        if '@my_company.com' in participant["email"]:
            if participant["email"] not in internal_employees:
                internal_employees.append(participant["email"])
        # Anyone who isn't in our company should be appended to external_prospects
        else:
            if participant["email"] not in external_prospects:
                external_prospects.append(participant["email"])
                this_meeting[participant["email"]] =  event["when"]["start_time"]

for employee in internal_employees:
    total_hours = 0
    for event in events:
        if employee in [participant["email"] for participant in event["participants"]]:
            # Nylas represents time as seconds since epoch time, we need to convert this to hours
            total_seconds = event["when"]["end_time"] - event["when"]["start_time"]
            total_hours += total_seconds / 60 / 60
    print("{} is spending {}% of their time in meetings this week".format(
        employee,
        ( total_hours / 25 ) * 100 ))
    

for prospect in external_prospects:
    contacts = nylas.contacts.where(email=prospect).all()
    if contacts:
        contact = contacts[0]
        # A contact can have multiple email addresses and phone numbers
        phone_number = next(iter(list(contact['phone_numbers'].values())), None)
        email = next(iter(list(contact['emails'].values())), None)

        print("Full Name: {} | Email: {} | Company Name: {} | Job Title: {} | Phone Number: {}".format(
            contact['given_name'] + " " + contact['surname'],
            email,
            contact['company_name'],
            contact['job_title'],
            phone_number,
            ))
   
for prospect in external_prospects:
    # Search the user's contact book for any that have the email address of the event participant
    contacts = nylas.contacts.where(email=prospect).all()
    if contacts:
        contact = contacts[0]
        contact.emails['work'] = [next(iter(list(contact['emails'].values())), None)][0]
        # Check to see if the contact already has a status statement in the notes field.
        if contact["notes"] and 'Status: ' in contact["notes"]:
            calendar_id = [ calendar['id'] for calendar in calendars if '<YOUR_CALENDAR_NAME>' in calendar['name'] ][0]
            all_events = nylas.events.where(calendar_id=calendar_id).all()
            for event in all_events:
                # Look for events on the calendar that include the prospect as a participant
                if prospect in [participant["email"] for participant in event["participants"]]:
                    # Return the dates we previously met with the prospect in a human-readable format
                    print("Met with {} on {}".format(
                        prospect,
                        datetime.datetime.fromtimestamp(event["when"]["start_time"]).strftime("%B %d, %Y - %H:%M:%S")
                        ))
        else:
            # If we've never met with this prospect before, record our upcoming meeting as the first meeting we've had with them.
            contact.notes = "Status: Prospect\nFirst Meeting: {}".format(
                    datetime.datetime.fromtimestamp(this_meeting[prospect]).strftime("%B %d, %Y - %H:%M:%S")
                    )
            try:
                contact.save() 
            except Exception as e:
                print(f"The contact {contact['given_name']} couldn't be updated {e}")
