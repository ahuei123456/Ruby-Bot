import tweepy, html, urllib.request, os, requests, bs4, re, linkutils
from os import path

twit_url = r'https://twitter.com/'


def get_links(status):
    links = []
    try:
        i_status = status.extended_tweet
        medias = i_status['extended_entities']['media']
    except (AttributeError, KeyError):
        if hasattr(status, 'extended_entities') and 'media' in status.extended_entities.keys():
            medias = status.extended_entities['media']

    try:
        for media in medias:
            if not media['type'] == 'video':
                links.append(media['media_url'])
            else:
                videos = media['video_info']['variants']
                bitrate = 0
                index = 0
                for i in range(0, len(videos)):
                    if videos[i]['content_type'] == 'video/mp4':
                        br = int(videos[i]['bitrate'])
                        if br > bitrate:
                            bitrate = br
                            index = i

                links.append(videos[index]['url'])
    except AttributeError:
        pass

    try:
        i_status = status.extended_tweet
        links = i_status['entities']['urls']
    except (AttributeError, KeyError):
        links = status.entities['urls']

    try:
        for link in links:
            ext = link['expanded_url']
            links.extend(linkutils.get_link(ext))
    except AttributeError:
        pass

    return links


def get_text(status):
    status = get_status(status)
    print(dir(status))
    try:
        status = status.extended_tweet
        print(dir(status))
        text = status['full_text']
        #full_text
        print('tweet is extended (01)')
    except AttributeError:
        try:
            text = status.full_text
            print('tweet is extended (02)')
        except AttributeError:
            text = status.text
            print('tweet is not extended')

    return html.unescape(text)


def get_status(status):
    if is_retweet(status):
        return get_status(status.retweeted_status)

    return status


def get_video(status):
    links = []
    try:
        if hasattr(status, 'extended_entities') and 'media' in status.extended_entities.keys():
            for media in status.extended_entities['media']:
                if media['type'] == 'video':
                    videos = media['video_info']['variants']
                    bitrate = 0
                    index = 0
                    for i in range(0, len(videos)):
                        if videos[i]['content_type'] == 'video/mp4':
                            br = int(videos[i]['bitrate'])
                            if br > bitrate:
                                bitrate = br
                                index = i

                    links.append(videos[index]['url'])
    except AttributeError:
        pass

    return links


def get_images(status):
    links = []
    try:
        i_status = status.extended_tweet
        medias = i_status['extended_entities']['media']
    except (AttributeError, KeyError):
        if hasattr(status, 'extended_entities') and 'media' in status.extended_entities.keys():
            medias = status.extended_entities['media']

    print(len(medias))

    try:
        for media in medias:
            print(media.keys())
            if not media['type'] == 'video':
                print(media['media_url'])
                links.append(media['media_url'])
            else:
                videos = media['video_info']['variants']
                bitrate = 0
                index = 0
                for i in range(0, len(videos)):
                    if videos[i]['content_type'] == 'video/mp4':
                        br = int(videos[i]['bitrate'])
                        if br > bitrate:
                            bitrate = br
                            index = i

                links.append(videos[index]['url'])
    except AttributeError:
        pass

    try:
        i_status = status.extended_tweet
        urls = i_status['entities']['urls']
    except (AttributeError, KeyError):
        urls = status.entities['urls']

    try:
        for link in urls:
            ext = link['expanded_url']
            links.extend(linkutils.get_link(ext))
    except AttributeError:
        pass

    return links


def make_url(username):
    return twit_url + username


def is_reply(status):
    return status.in_reply_to_user_id is not None and status.in_reply_to_user_id != status.user.id


def is_retweet(status):
    return hasattr(status, 'retweeted_status')


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


def get_user(api_twitter, user_id):
    return api_twitter.get_user(user_id)


def get_user_id(api_twitter, user_id: str):
    return api_twitter.get_user(user_id).id


def get_tweets(api_twitter, username: str, num=1):
    statuses = list(tweepy.Cursor(api_twitter.user_timeline, id=id).items(num))
    return statuses


def get_user(api_twitter, user_id):
    return api_twitter.get_user(user_id)




