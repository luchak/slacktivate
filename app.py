from flask import Flask, Response, request
from lib.paper import append
import json
import logging
import os
import requests
import sqlite3
import urllib.parse
from slackclient import SlackClient

import db

app = Flask(__name__)
app.config.from_envvar('SLACKTIVATE_CONFIG')


# Super hack-ish way to get a URL for a particular message
def url_for_message(channel, message):
    return app.config['SLACK_DOMAIN'] + '/archives/' + channel + '/p' + ''.join(message['ts'].split('.'))

def get_slack_client():
    return SlackClient(app.config['SLACK_TOKEN'])

def decode_slack_encoding(text):
    ret = text;
    ret = '>'.join(ret.split('&gt;'))
    ret = '<'.join(ret.split('&lt;'))
    ret = '&'.join(ret.split('&amp;'))
    return ret

def get_username_from_id(user_id):
    result = get_slack_client().api_call(
        'users.info',
        user=user_id
    )
    try:
        return result['user']['name']
    except:
        return 'Slacktivate'

def get_channel_name_from_id(channel_id):
    result = get_slack_client().api_call(
        'channels.info',
        channel=channel_id
    )
    return result['channel']['name']


def handle_twitter(channel, user, message):
    message_text = decode_slack_encoding(message['text'])
    tweet_intent_url = 'https://twitter.com/intent/tweet?{}'.format(
        urllib.parse.urlencode({'text': message_text}),
    );
    tweet_button_action = json.dumps([
        {
            "fallback": "You are unable to choose an option",
            "actions": [
                {
                    "type": "button",
                    "text": "Compose tweet :twitter:",
                    "url": tweet_intent_url
                },
                {
                    "type": "button",
                    "text": "View source :slack:",
                    "url": url_for_message(channel, message)
                }
            ]
        }
    ])
    try:
        original_poster = message['user']
    except:
        return
    result = get_slack_client().api_call(
        'chat.postMessage',
        channel='tweetdrafts',
        as_user=False,
        text='Got a tweet suggestion by {} on {}\'s post in {}: \"{}\"'.format(
            '<@{}>'.format(user),
            '<@{}>'.format(original_poster),
            '<#{}>'.format(channel),
            message['text']),
        attachments=tweet_button_action
    )

def handle_faq(channel, user, message):
    url = url_for_message(channel, message)
    try:
        original_poster = message['user']
    except:
        return
    append(app.config['DROPBOX_ACCESS_TOKEN'], 
        '# [Message from {} in #{}]({})'.format(
            get_username_from_id(original_poster),
            get_channel_name_from_id(channel),
            url)
        + '\n\n' + message['text'])

def get_message_from_item(message_item):
    if message_item['type'] != 'message':
        raise ValueError('Cannot fetch non-message item')

    timestamp = float(message_item['ts'])

    history = get_slack_client().api_call(
        'channels.history',
        channel=message_item['channel'],
        count=10,
        latest=timestamp + 1,
        oldest=timestamp - 1,
    )

    for message in history['messages']:
        if message['ts'] == message_item['ts']:
            return message

    return None


EMOJI_ROUTES = {
    'twitter': handle_twitter,
    'faq': handle_faq,
}


@app.route('/')
def hello_world():
    return 'Hello, Matt!'


@app.route('/event', methods=['POST'])
def handle_event():
    event = request.json
    if event['type'] == 'url_verification':
        return Response(event['challenge'], mimetype='text/plain')
    elif event['type'] == 'event_callback':
        inner_event = event['event']
        if inner_event['type'] == 'reaction_added':
            route = EMOJI_ROUTES.get(inner_event['reaction'])
            if route:
                message = get_message_from_item(inner_event['item'])
                conn = db.Connection()
                if not conn.has_run(inner_event):
                    message = get_message_from_item(inner_event['item'])
                    user = inner_event['user']
                    channel = inner_event['item']['channel']
                    route(channel, user, message)
                    conn.mark_run(inner_event)
            else:
                logging.info('Unknown emoji:', inner_event['reaction'])
        else:
            logging.warn('Unknown inner event type:', inner_event['type'])
    else:
        logging.warn('Unknown outer event type:', event['type'])
    return ''
