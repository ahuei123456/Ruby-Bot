import tweepy, time, html, urllib.request, os, re, bs4, requests
from cogs.utils import utilities

user_encode = ["Username: {0.screen_name}",
                "Display name: {0.name}",
                "ID: {0.id_str}",
                "Description: {0.description}",
                "Current profile image: {0.profile_image_url}",
                "Current banner image: {0.profile_banner_url}",
                "Tweets: {0.statuses_count}",
                "Followers: {0.followers_count}",
                "Following: {0.friends_count}",
                "Protected: {0.protected}"]

user_url = "URL: {}"

listener = None

twit_url = r'https://twitter.com/'

class TweetListener(tweepy.StreamListener):

    def __init__(self, id):
        super(TweetListener, self).__init__()

        self.statuses=list()
        self.id = id

    def on_status(self, status):
        try:
            text = html.unescape(status.text)

            if is_reply(status):
                return
            if not str(status.user.id) in self.id:
                return

            self.statuses.append(status)
        except Exception as e:
            print(e)

    def on_timeout(self):
        print('timeout')

    def on_error(self, status_code):
        print(status_code)

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


def init_stream(id):
    global listener
    global poster
    # ll_wikia 2734031000
    # mkydyrea 3299062544
    # LLupdates 4423137133
    # ll_extra 739117766100189184
    # lovelive_staff 347849994
    # lovelive_sif 1346933186
    # ischyrb 357915189

    listener = TweetListener(id)
    poster = tweepy.Stream(auth=auth, listener=listener)
    poster.filter(follow=id, track=['#千歌ちゃんクソコラグランプリ'], async=True)


def kill_stream():
    global poster

    poster.disconnect()
    time.sleep(3)


def restart_stream(id):
    global listener
    global poster

    listener = TweetListener(id)
    poster = tweepy.Stream(auth=auth, listener=listener)
    poster.filter(follow=id, track=['#千歌ちゃんクソコラグランプリ'], async=True)


def stream_new_tweets():
    return listener.get_status()


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
    encoded = ''
    for string in user_encode:
        try:
            encoded += string.format(user) + '\n'
        except AttributeError:
            pass

    encoded += user_url.format(make_url(user.screen_name))
    return encoded.strip()


def is_reply(status):
    return status.in_reply_to_user_id is not None and status.in_reply_to_user_id != status.user.id


def is_retweet(status):
    return hasattr(status, 'retweeted_status')


def make_url(username):
    return twit_url + username


def archive(userid, filename='saved.txt'):
    with open(filename, 'a') as save:
        for status in tweepy.Cursor(api_twitter.user_timeline, id=userid).items(200):
            save.write((html.unescape(encode_tweet(status))))


def yohane_compare():
    wikia = api_twitter.get_status(752880219300605953)
    llu = api_twitter.get_status(752880220823228416)
    aikyan = api_twitter.get_status(752880230902005760)
    secll = api_twitter.get_status(752880233334788096)

    print('wikia: ' + wikia.created_at.strftime('%c'))
    print('llu: ' + llu.created_at.strftime('%c'))
    print('aikyan: ' + aikyan.created_at.strftime('%c'))
    print('secll: ' + secll.created_at.strftime('%c'))


def save_hashtag(hashtag):
    for status in tweepy.Cursor(api_twitter.search, q=hashtag).items(1000):
        try:
            for media in status.extended_entities['media']:
                print(media['media_url'])
                urllib.request.urlretrieve(media['media_url'], os.path.join(os.getcwd(), os.path.join('files', 'riko_meme'), media['media_url'].link.split('/')[-1]))
        except AttributeError:
            pass



def parse_input(id_status):
    id = id_status.split('/')
    status = api_twitter.get_status(id[len(id) - 1])
    return status

init_twitter()
#yohane_compare()
#init_stream()