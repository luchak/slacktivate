from flask import Flask, Response, request
import json
import requests
from slackclient import SlackClient

app = Flask(__name__)
app.config.from_pyfile('slacktivate.cfg')

def get_message_from_item(message_item):
    if message_item['type'] != 'message':
        raise ValueError('Cannot fetch non-message item')

    timestamp = float(message_item['ts'])

    sc = SlackClient(app.config['SLACK_TOKEN'])
    history = sc.api_call(
        'channels.history',
        channel=message_item['channel'],
        count=10,
        latest=timestamp + 1,
        oldest=timestamp -1 
    )

    for message in history['messages']:
        if message['ts'] == message_item['ts']:
            return message

    return None


@app.route('/')
def hello_world():
    return 'Hello, Matt!'

@app.route('/event', methods=['POST'])
def handle_event():
    print('CONFIG')
    print(app.config)
    event = request.json
    if event['type'] == 'url_verification':
        return Response(event['challenge'], mimetype='text/plain')
    elif event['type'] == 'event_callback':
        inner_event = event['event']
        if inner_event['type'] == 'reaction_added':
            message = get_message_from_item(inner_event['item'])
            print('reaction message text: {}'.format(message['text']))
            return ''
        else:
            print('Unknown inner event type:')
            print(inner_event)
            return ''
    else:
        print('Unknown outer event type:')
        print(event)
        return ''
