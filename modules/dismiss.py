#!/usr/bin/python3
import json
import os
def dismiss(phenny, input):
    try:
        opted_out_list = open(os.getenv('HOME') + '/.phenny/opted_out_of_matrix_message.json', 'r')
        opted_out_of_m = json.load(opted_out_list)
        opted_out_list.close()
    except:
        opted_out_of_m = []

    opted_out_of_m.append(input.nick)

    try:
        opted_out_list = open(os.getenv('HOME') + '/.phenny/opted_out_of_matrix_message.json', 'w+')
        json.dump(opted_out_of_m, opted_out_list)
        phenny.say('I won\'t tell you again.')
    except Exception as e:
        phenny.say('Sorry, an error occurred.')
        raise e

dismiss.commands = ['dismiss']
dismiss.priority = 'medium'
