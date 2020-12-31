## Google Sheet Shopping List
A MagTag app that uses Google Sheets API, a Google service account, JWT authentication and MagTag deep sleep.

## Steps
1. This project will use a Google service account. You'll grant your service account read access to your Google Sheet so that the Sheet remains private. In order to create our service account, we first need a Google API project. Follow [this link](https://console.developers.google.com/flows/enableapi?apiid=sheets) to get started creating your Google Cloud project.
2. In the dropdown, leave `Create a project` selected and click the blue `Continue` button.
3. Your project will be created and the Google Sheets API will be enabled. Now click the blue `Go to credentials` button.
4. Next you are taken to a wizard asking you some questions about your project. Ignore these questions and look further up where it says `If you wish you can skip this step and create an API key, client ID, or service account.`. Click on `service account` link.
5. You'll be brought to a list of service accounts for your project which is empty because you haven't created one yet. Click `CREATE SERVICE ACCOUNT`.
6. Give your service account a name that you like. Once you a type a name the email address will also be populated which saves you some typing. Click `Create`.
7. We can skip the optional Steps 2 and 3 and just click the blue `DONE` button at the bottom.
8. Now we have a service account but we need to be able to authenticate. Copy the Email address into your clipboard, you'll need it in just a minute. The email address will look something like `service-account-name@project-name.iam.gserviceaccount.com`.
9. On a Mac or Linux computer, you can run [gen_pk.py](https://github.com/jay0lee/MagTag-projects/blob/main/Google_Sheet_Shopping_List/gen_pk.py) which will generate the private key and public certificate for your service account. These act sort of like the password to authenticate the service account to Google. Run the script with a command like:<br>
```python3 gen_pk.py <service account email>```
10. If you get an error about needing the cryptography library, you can install it with:<br>
```pip3 install cryptography```<br>and then rerun gen_pk.py.
11. gen_pk.py will generate a private key and it's public certificate. We'll store the private key in secrets.py but first we'll upload the public key to Google.. Copy the entire certificate value and then go back into the Cloud console. Be sure that you copy the BEGIN CERTIFICATE / END CERTIFICATE lines also, not just the random characters. The exact text you need to copy will look something like:<br>
```
-----BEGIN CERTIFICATE-----
MIIB5TCCAU6gAwIBAgIUNdAh4aKwBR1wm8Ff0lX69tf625QwDQYJKoZIhvcNAQEL
BQAwETEPMA0GA1UEAwwGYWJjMTIzMCAXDTIwMTIyMzEzNDI0N1oYDzMwMjAwNDI1
<more lines of random characters...>
trPaqWBddU6r
-----END CERTIFICATE-----
```
12. with the public certificate copied go back into your browser and Cloud console. You should still be at the list of service accounts and showing the service account you created. In the `Key ID` column your service account will show `No keys`. Click the service account email address and scroll down to the `Keys` section.
13. Click `ADD KEY` and `Upload existing key`.
14. In the textbox that says `Upload existing key` paste in the certificate text you copied from the Python script. Click `UPLOAD`.
15. Once uploaded your new Key will show in the list and be assigned a unique alphanumeric ID. Copy that ID, we'll need to paste it back into the gen_pk.py script.
16. Enter the key ID you copied from the cloud console into the still runnig gen_pk.py Python script and hit enter. Now the script will print out the exact lines you need to add to your `secrets.py` file. These include the `private_key`, `private_key_id` and `service_account_email` attributes.
17. Download the [newest CircutiPython library bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases) (bundle date Dec 24, 2020 or newer) and copy following libraries to the MagTag's lib/ folder:
```
adafruit_bitmap_font/
adafruit_display_shapes/
adafruit_display_text/
adafruit_hashlib/
adafruit_io/
adafruit_magtag/
adafruit_portalbase/
adafruit_rsa/
adafruit_binascii.mpy
adafruit_fakerquests.mpy
adafruit_jwt.mpy
adafruit_logging.mpy
adafruit_requests.mpy
neopixel.mpy
simpleio.mpy
```
18. Create your Google Sheet by going to [sheets.new](https://sheets.new) (.new is a cool trick for Google Docs. Also try [docs.new](docs.new), [slides.new](slides.new), [forms.new](forms.new)...)
19. The sheet is very basic. Add some kind of header in A1 like "List" and then list your shopping items in column A. From your Sheet's URL copy the Sheet ID value.
20. Share the Google Sheet with your service account email address you copied earlier. The service account only needs reader access.
21. Copy the ID of the Sheet. If the browser URL when you open the Sheet is `https://docs.google.com/spreadsheets/d/1Q8RlCI3glZA7gXB6Wmdmkq1zS29j3_LFqc9x2qRan00/edit#gid=0` then your Sheet ID is `1Q8RlCI3glZA7gXB6Wmdmkq1zS29j3_LFqc9x2qRan00`
22. Copy [code.py](https://raw.githubusercontent.com/jay0lee/MagTag-projects/main/Google_Sheet_Shopping_List/code.py) to your device. You need to edit the file and set `SHEET_ID='<ID from above>'`. There are a few other values you may wish to customize.

Save and run!
