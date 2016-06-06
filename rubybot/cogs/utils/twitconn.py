import tweepy
import bs4
import requests

from cogs.utils import utilities

user_encode = "Username: {0.screen_name}\nDisplay name: {0.name}\nCurrent profile image: {0.profile_image_url}\nCurrent banner image: {0.profile_banner_url}"
wikia_listener = None

class LLWikiaListener(tweepy.StreamListener):

    def __init__(self, id):
        super(LLWikiaListener, self).__init__()

        self.statuses=list()
        self.id = id

    def on_status(self, status):

        if is_reply(status):
            return
        if not str(status.user.id) in self.id:
            return
        user = status.user.name
        text = status.text
        send = "Latest tweet by {0}: {1}\n".format(user, text)
        try:
            for media in status.extended_entities['media']:
                send += media['media_url'] + ' '
        except AttributeError:
            pass

        self.statuses.append(send)

    def get_status(self):
        statuses = self.statuses[:]
        self.statuses.clear()
        return statuses


def init_twitter():
    global api_twitter
    global auth
    credentials = utilities.load_credentials()

    c_key = credentials['client_key']
    c_secret = credentials['client_secret']
    a_token = credentials['access_token']
    a_secret = credentials['access_secret']
    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_secret)

    api_twitter = tweepy.API(auth)


def init_strim():
    global wikia_listener
    # ll_wikia 2734031000
    # mkydyrea 3299062544
    # LLupdates 4423137133
    # ll_extra 739117766100189184
    # lovelive_staff 347849994
    # lovelive_sif 1346933186
    id = ['2734031000', '3299062544', '4423137133', '347849994', '1346933186', '739117766100189184']
    wikia_listener = LLWikiaListener(id)
    wikia_poster = tweepy.Stream(auth=auth, listener=wikia_listener)
    wikia_poster.filter(follow=id, async=True)


def stream_new_tweets():
    return wikia_listener.get_status()


def get_tweets(username: str, num=1):
    statuses = list(tweepy.Cursor(api_twitter.user_timeline, id=id).items(num))
    return statuses


def get_filtered_tweets(username: str, num=1):
    statuses = get_tweets(username, num)
    statuses = strip_replies(statuses)
    statuses = strip_retweets(statuses)
    return statuses


def strip_retweets(tweets):
    stripped = list()
    for tweet in tweets:
        if not is_retweet(tweet):
            stripped.append(tweet)

    return stripped


def strip_replies(tweets):
    stripped = list()
    for tweet in tweets:
        if not is_reply(tweet):
            stripped.append(tweet)

    return stripped


def get_user(user_id):
    return api_twitter.get_user(user_id)


def get_user_info(user_id):
    user = get_user(user_id)
    info = encode_user(user)
    return info


def get_user_id(self, user_id: str):
    return api_twitter.get_user(user_id).id


def encode_tweet(tweet):
    user = tweet.user.name
    text = tweet.text
    send = "Tweet by {0}: {1}\n".format(user, text)
    try:
        for media in tweet.extended_entities['media']:
            send += media['media_url'] + ' '
    except AttributeError:
        pass

    return send


def encode_user(user):
    return user_encode.format(user)


def is_reply(status):
    return status.in_reply_to_user_id is not None and status.in_reply_to_user_id != status.user.id


def is_retweet(status):
    return hasattr(status, 'retweeted_status')


init_twitter()
init_strim()