from bs4 import BeautifulSoup
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle
import requests
from selenium import webdriver
import smtplib

# Import password from secrets.py file
from secrets import gmail_password

# Login credentials for email
gmail_user = 'wombatsaresneaky@gmail.com'

# Set up Chrome Driver for Selenium to Load Webpage
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)

# Write out current date & time
print('\n')
now = datetime.now()
current_time = now.strftime("%m/%d/%Y %H:%M:%S")
print("Current Time =", current_time)


# Script to send email with unit details
def send_email(units):

    sent_from = gmail_user
    to_list = ['mt.toth@gmail.com', 'margaretblack89@gmail.com']
    email = 'mt.toth@gmail.com'
    subject = 'New apartments available at Venue!'

    body = ''
    for unit_dict in units:
    	unit = units.get(unit_dict)
    	name = unit_dict
    	beds = unit.get('beds')
    	sq_feet = unit.get('sq_feet')
    	avail = unit.get('avail')
    	pricing = unit.get('pricing')

    	unit_text = name + ' ' + ' - ' + str(beds) + ' Beds, ' + sq_feet + ' : ' + str(avail) + ' Units Available ' + pricing + '\n\n'
    	body = body + unit_text

    body = body + 'See more: https://www.venueon16.com/availability/'
    message = body
    
    for to in to_list:
	    msg = MIMEMultipart()
	    msg["From"] = email
	    msg["To"] = to
	    msg["Subject"] = subject

	    msg.attach(MIMEText(message, 'plain'))

	    try:
	        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	        smtp_server.ehlo()
	        smtp_server.login(gmail_user, gmail_password)
	        email_text = msg.as_string()
	        smtp_server.sendmail(sent_from, to, email_text)
	        smtp_server.close()
	        print ("Email sent successfully!")
	    except Exception as ex:
	        print ("Something went wrong….",ex)



# Get data from URL
URL = "https://www.venueon16.com/availability/"
page = requests.get(URL)
driver.get(URL)
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")


# Find specific unit details
results = soup.find(id="unit-listing")
apartments = results.find_all("div", class_="available-unit-grid")


# Loop through apartments in list
units = {}
send = False
for apartment in apartments:
    unit_name = apartment.find("h2").text
    unit_info = apartment.find("h3", class_="listing-unit-info").text
    unit_avail = apartment.find("h3", class_="listing-unit-info availprice").text

    split_location = unit_info.find('Bath') + len('Bath')
    beds_baths = unit_info[0:split_location]
    sq_feet = unit_info[split_location:]

    if beds_baths[0] == 'S':
            num_beds = 0
    else:
        num_beds = int(beds_baths[0])

    num_available = int(unit_avail[0])
    pricing_split = unit_avail.find('Available') + len('Available')
    pricing = unit_avail[pricing_split:]

    if num_available == 0:
        # Ignore
        continue
    elif num_beds != 2:
        continue
    else:
        send = True
        unit = {
            "beds": num_beds,
            "sq_feet": sq_feet,
            "avail": num_available,
            "pricing": pricing
        }

        units[unit_name] = unit
        #print(units)
        print("Unit: " + unit_name)
        print(beds_baths)
        print(num_beds)
        print(sq_feet)
        print("Available: " + str(num_available))
        print(pricing, end="\n"*2)


# Open the stored units dictionary
pickle_file = "/Users/michaeltoth/dev/experiments/apartments/apartments.pkl"
stored_units = pickle.load(open(pickle_file, "rb"))

# Compare to the current units dictionary, send email if changed
if(stored_units != units):
    print('Units have changed!')
    print(units)
    print(stored_units)

    # write the python object (dict) to pickle file
    f = open(pickle_file,"wb")
    pickle.dump(units,f)

    # close file
    f.close()

    if send == True:
        send_email(units)
else:
    print('Units unchanged. Not sending email')






