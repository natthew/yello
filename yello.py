import oauth2
import optparse
import urllib
import urllib2
import json

def parse_message(req):
    term, address = req.split('near')
    return term.strip(), address.strip()


def authenticate_request(url, consumer_key, consumer_secret, token,
                         token_secret):
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    oauth_request = oauth2.Request('GET', url, {})
    oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                           'oauth_timestamp': oauth2.generate_timestamp(),
                           'oauth_token': token,
                           'oauth_consumer_key': consumer_key})

    token = oauth2.Token(token, token_secret)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer,
                               token)
    signed_url = oauth_request.to_url()
    return signed_url


def request_response(signed_url):
    try:
        conn = urllib2.urlopen(signed_url)
        try:
            response = json.loads(conn.read())
        finally:
            conn.close()
    except urllib2.HTTPError, error:
        response = json.loads(error.read())

    return response


def build_url(host, path, **kwargs):
    base_url = "http://" + host + path + "?"
    url_args = []
    print kwargs
    for key, value in kwargs.items():
        url_args.append(key + "=" + urllib.quote_plus(value))
    url = base_url + "&".join(url_args)
    return url


if __name__ == "__main__":
    oauth_stuff = (consumer_key, consumer_secret, token, token_secret) = [
        x.strip() for x in open("yelp.auth").readlines()]
    host = "api.yelp.com"
    path = "/v2/search"
    while True:
        print "Type your request, then press enter. Press ctrl-C to go home."
        message = raw_input("> ")
        term, location = parse_message(message)
        url = build_url(host, path, term=term, location=location)
        signed_url = authenticate_request(url, *oauth_stuff)
        response = request_response(signed_url)
        if 'businesses' in response:
            first_business = response['businesses'][0]
            name = first_business['name']
            print name
        else:
            print "Undefined Error! Fix me!"
