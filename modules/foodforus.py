#!/usr/bin/python3
"""
foodforus.py - foodforus module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

from tools import GrumbleError
import hashlib
import json
import web

API_URL = 'https://foodfor.vtluug.org'


def _sign_vote(api_key, args):
    data = "ffu1"
    for k, v in sorted(args.items()):
        if k == 'sig':
            continue
        data += '{0}{1}'.format(k, v)
    data += api_key
    h = hashlib.sha256()
    h.update(data.encode('utf-8'))
    return h.hexdigest()


def food(phenny, input):
    """.food"""
    key = input.group(2) or input.sender
    try:
        req = web.get(API_URL + '/food/' + web.quote(key.strip()))
        data = json.loads(req)
    except:
        raise GrumbleError("Uh oh, I couldn't contact foodforus. HOW WILL WE "\
                "EAT NOW‽")

    restaurants = data['restaurants'][:4]
    times = data['times'][:4]

    restr = ", ".join(["{0} ({1})".format(r[0], r[1]) for r in
        restaurants])
    tistr = ", ".join(["{0} ({1})".format(t[0], t[1]) for t in times])

    if len(restr) > 0 and len(tistr) > 0:
        return phenny.say("{0} at {1}".format(restr, tistr))
    else:
        return phenny.say("Sorry, people need to vote before we can food!")
food.rule = (['food'], r'(.*)')


def foodvote(phenny, input):
    """.foodvote"""
    if not input.group(2) or not input.group(3):
        return phenny.reply("You need to specify a place and time, as in "\
                ".foodvote hokie haus 18:45")

    key = input.group(4) or input.sender
    postdata = {
        'user': input.nick,
        'restaurant': input.group(2),
        'start': input.group(3),
        'key': key.strip(),
    }
    postdata['sig'] = _sign_vote(phenny.config.foodforus_api_key, postdata)

    try:
        req = web.post(API_URL + '/vote', postdata)
        data = json.loads(req)
    except:
        raise GrumbleError("Uh oh, I couldn't contact foodforus. HOW WILL WE "\
                "EAT NOW‽")

    if 'error' in data:
        phenny.reply(data['error'])
    else:
        phenny.reply("Your vote has been recorded.")
foodvote.rule = (['foodvote'], r'(.*) (\d{2}:\d{2})( .*)?')


def pickfood(phenny, input):
    key = input.group(2) or input.sender
    try:
        req = web.get(API_URL + '/food/' + web.quote(key.strip()))
        data = json.loads(req)
    except:
        raise GrumbleError("Uh oh, I couldn't contact foodforus. HOW WILL WE "\
                "EAT NOW‽")

    if len(data['restaurants']) > 0 and len(data['times']) > 0:
        restaurant = data['restaurants'][0]
        time = data['times'][0]

        phenny.say("Food is {place} ({place_votes} votes) at {time} "\
                "({time_votes} votes). Happy fooding!".format(place=restaurant[0],
                place_votes=restaurant[1], time=time[0], time_votes=time[1]))
    else:
        phenny.say("Sorry, people need to vote before we can food!")
pickfood.rule = (['pickfood'], r'(.*)')
