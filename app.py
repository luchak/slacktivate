from flask import Flask, Response, request
import json
import logging
import requests
from urllib.parse import urlencode, quote_plus
from slackclient import SlackClient

app = Flask(__name__)
app.config.from_pyfile('slacktivate.cfg')

def get_slack_client():
    return SlackClient(app.config['SLACK_TOKEN'])

def handle_twitter(channel, message):
    tweet_intent_url = 'https://twitter.com/intent/tweet?text={}'.format(message['text']);
    tweet_button_action = json.dumps([
        {
            "fallback": "You are unable to choose an option",
            "actions": [
                {
                    "type": "button",
                    "text": "Compose tweet :twitter:",
                    "url": tweet_intent_url
                }
            ]
        }
    ])
    result = get_slack_client().api_call(
        'chat.postMessage',
        channel='tweetdrafts',
        as_user=False,
        text='Got a tweet suggestion from @{} in #{}: \"{}\"'.format(
            'cchio',
            channel,
            message['text']),
        attachments=tweet_button_action
    )
    payload = {'text': message['text']}

def handle_faq(channel, message):
    result = get_slack_client().api_call(
        'chat.postMessage',
        channel=channel,
        as_user=False,
        text='Got a FAQ suggestion: {}'.format(message['text'])
    )

def get_message_from_item(message_item):
    if message_item['type'] != 'message':
        raise ValueError('Cannot fetch non-message item')

    timestamp = float(message_item['ts'])

    history = get_slack_client().api_call(
        'channels.history',
        channel=message_item['channel'],
        count=10,
        latest=timestamp + 1,
        oldest=timestamp -1,
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
                route(inner_event['item']['channel'], message)
            else:
                logging.info('Unknown emoji:', inner_event['reaction'])
            return ''
        else:
            logging.warn('Unknown inner event type:', inner_event['type'])
            return ''
    else:
        logging.warn('Unknown outer event type:', event['type'])
        return ''
