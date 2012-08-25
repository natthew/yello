import datetime
import json
import urllib
import urllib2

import oauth2
from flask import Flask
from twilio.rest import TwilioRestClient

MY_PHONE_NUMBER = '+13232489357'

app = Flask(__name__)

@app.route("/yello.xml")
def hello():
    twilio_client.respond_to_message()
    return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

class TwilioResponseClient(object):
    def __init__(self, keys, phone_number):
        self.sid = keys['sid']
        self.token = keys['token']
        self.phone_number = phone_number
        self.client = TwilioRestClient(self.sid, self.token)
        self.message_cache = []

    def respond_to_message(self):
        incoming_messages = self.client.sms.messages.list(
            to=self.phone_number, date_sent=datetime.date.today())
#        latest_request = incoming_messages[0]
#        latest_message = latest_request.body
#        incoming_number = latest_request.from_
        latest_message = 'derp'
        incoming_number = '+16313386254'
        #TODO: handle multiple messages / race conditions
        query, location, filters = yelp_client.parse_message(latest_message)
        search_result = yelp_client.search(query, location, filters)
        self.client.sms.messages.create(to=incoming_number,
            from_=self.phone_number, body=search_result)


class YelpAPIClient(object):
    def __init__(self, keys):
        self.consumer = oauth2.Consumer(keys['consumer_key'], keys['consumer_secret'])
        self.token = oauth2.Token(keys['token'], keys['token_secret'])

    def parse_message(self, message):
        #TODO: implement me
        return "pizza", "San Francisco", {}

    def authenticate_request(self, url):
        request = oauth2.Request('GET', url, {})
        request.update({
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': self.token.key,
            'oauth_consumer_key': self.consumer.key
        })
        request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), self.consumer, self.token)
        signed_url = request.to_url()
        return signed_url

    def build_url(self, args):
        base_url = "http://api.yelp.com/v2/search?"
        url_args = []
        for name, value in args.iteritems():
            url_args.append("{0}={1}".format(name, urllib.quote_plus(value)))
        url = base_url + "&".join(url_args)
        return url

    def search(self, query, location, filters={}):
        args = {'term': query, 'location': location}
        for name, value in filters:
            args[name] = value
        url = self.build_url(args)
        print url
        signed_url = self.authenticate_request(url)

        try:
            conn = urllib2.urlopen(signed_url)
        except urllib2.URLError:
            return "Sorry, we're experiencing some technical difficulties. Try again later."
        try:
            response = json.loads(conn.read())
        except ValueError:
            conn.close()
            return "Sorry, Yelp appears to be having some issues. Try again later."

        businesses = response.get('businesses')
        if not businesses:
            return "We couldn't find any results in that area. Try a different search."
        business = businesses[0]
        name = business['name']
        address = ' '.join(business['location']['display_address'])
        return "{0} at {1}".format(name, address)


if __name__ == "__main__":
    auth = json.load(open('auth'))
    yelp_client = YelpAPIClient(auth['yelp'])
    twilio_client = TwilioResponseClient(auth['twilio'], MY_PHONE_NUMBER)
    app.run(debug=True)