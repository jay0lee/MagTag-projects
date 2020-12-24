"""
Google Sheets MagTag example: Shopping List.
Uses a Google service account and private key to get authenticated access
to the Google Sheet. Deep sleeps and only redraws on changes to the Sheet.
Fonts from Xorg project.
"""

# pylint: disable=import-error, line-too-long
import alarm
import time
import rtc
from adafruit_display_shapes.rect import Rect
from adafruit_magtag.magtag import MagTag
from adafruit_jwt import JWT
from adafruit_hashlib import sha1

from secrets import secrets

# CONFIGURABLE SETTINGS and ONE-TIME INITIALIZATION ------------------------
SHEET_ID = ''
RANGE = 'A2:A'
JSON_URL = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?fields=values'.format(SHEET_ID, RANGE)
DEEP_SLEEP_MINUTES = 10

TWELVE_HOUR = True # If set, show 12-hour vs 24-hour (e.g. 3:00 vs 15:00)
DD_MM = False      # If set, show DD/MM instead of MM/DD dates

# SOME UTILITY FUNCTIONS ---------------------------------------------------

def hh_mm(time_struct, twelve_hour=True):
    """ Given a time.struct_time, return a string as H:MM or HH:MM, either
        12- or 24-hour style depending on twelve_hour flag.
    """
    if twelve_hour:
        if time_struct.tm_hour > 12:
            hour_string = str(time_struct.tm_hour - 12) # 13-23 -> 1-11 (pm)
        elif time_struct.tm_hour > 0:
            hour_string = str(time_struct.tm_hour) # 1-12
        else:
            hour_string = '12' # 0 -> 12 (am)
    else:
        hour_string = '{hh:02d}'.format(hh=time_struct.tm_hour)
    return hour_string + ':{mm:02d}'.format(mm=time_struct.tm_min)


# NET / GRAPHICS INITIALIZATION ----------------------------------------------

MAGTAG = MagTag(rotation=0) # Portrait (vertical) display
MAGTAG.network.connect()

# First text label (index 0) is day of week -- empty for now, is set later
MAGTAG.add_text(
    text_font='/fonts/helvB24.pcf',
    text_position=(MAGTAG.graphics.display.width // 2, 4),
    line_spacing=1.0,
    text_anchor_point=(0.5, 0), # Center top
    is_data=False,              # Text will be set manually
)

# Second (index 1) is task list -- again, empty on start, is set later
MAGTAG.add_text(
    text_font='/fonts/ncenR14.pcf',
    text_position=(3, 36),
    line_spacing=1.0,
    text_anchor_point=(0, 0), # Top left
    is_data=False,            # Text will be set manually
)

# Add 14-pixel-tall black bar at bottom of display. It's a distinct layer
# (not just background) to appear on top of task list if it runs long.
MAGTAG.graphics.splash.append(Rect(0, MAGTAG.graphics.display.height - 14,
                                   MAGTAG.graphics.display.width,
                                   MAGTAG.graphics.display.height, fill=0x0))

# Center white text (index 2) over black bar to show last update time
MAGTAG.add_text(
    text_font='/fonts/helvB12.pcf',
    text_position=(MAGTAG.graphics.display.width // 2,
                   MAGTAG.graphics.display.height - 1),
    text_color=0xFFFFFF,
    text_anchor_point=(0.5, 1), # Center bottom
    is_data=False,              # Text will be set manually
)

try:
    print('Updating time')
    MAGTAG.get_local_time()
    NOW = rtc.RTC().datetime
    iat = time.mktime(NOW) + (3600 * 5)
    exp = iat + 3600
    claim = {
        'iss': secrets['service_account_email'],
        'sub': secrets['service_account_email'],
        'aud': 'https://sheets.googleapis.com/',
        'iat': str(iat),
        'exp': str(exp),
    }
    jwt_headers = {'kid': secrets['private_key_id']}
    jwt = JWT.generate(claim,
                       secrets['private_key'],
                       algo='RS256',
                       headers=jwt_headers)
    headers = {'Authorization': 'Bearer {}'.format(jwt)}
    print('Fetching Google Sheet range...')
    RESPONSE = MAGTAG.network.fetch(JSON_URL, headers=headers)
    print(RESPONSE.status_code)
    if RESPONSE.status_code != 200:
        print('ERROR {} getting API data. Will try again later.'.format(RESPONSE.status_code))

    JSON_DATA = RESPONSE.json()
    print('OK')

    ITEM_LIST = []
    for row in JSON_DATA.get('values', []):
        for cell in row:
            ITEM_LIST.append(cell)
    ITEMS = '\n'.join(ITEM_LIST)

    # Calculate SHA-1 hash of items and retrieve old calculation from sleep
    # memory. If they match the Sheet list hasn't changed and we don't need
    # to redraw.
    m = sha1()
    m.update(ITEMS)
    current_hash = m.hexdigest()
    old_hash = alarm.sleep_memory[:40].decode()
    if current_hash != old_hash: 
        print('Need to redraw display...')

        MAGTAG.set_text('List ', auto_refresh=False)

        # Set the "Updated" date and time label
        if DD_MM:
            DATE = '%d/%d' % (NOW.tm_mday, NOW.tm_mon)
        else:
            DATE = '%d/%d' % (NOW.tm_mon, NOW.tm_mday)
        MAGTAG.set_text('Updated %s %s' % (DATE, hh_mm(NOW, TWELVE_HOUR)),
                        2, auto_refresh=False)

        MAGTAG.set_text(ITEMS, 1) # Update list, refresh display
        
        alarm.sleep_memory[:40] = bytearray(current_hash)
    else:
        print('no need to update, I\'m going back to bed')

except RuntimeError as error:
    # If there's an error above, no harm, just try again after a deep sleep.
    # Usually it's a common network issue or time server hiccup.
    print('retrying later ', error)

print('sleeping for {} minutes...'.format(SLEEP_MINUTES))
# Go the f* to sleep
sleep_seconds = SLEEP_MINUTES * 60
al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + sleep_seconds)
alarm.exit_and_deep_sleep_until_alarms(al)
