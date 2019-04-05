import discord, html, twitutils


def encode_tweet(tweet):
    title = "Tweet by {0}".format(tweet.user.name)
    type = "rich"
    description = tweet.text

    user = tweet.user.name
    text = tweet.text
    send = "Tweet by {0}: {1}\n".format(user, text)
    try:
        for media in tweet.extended_entities['media']:
            send += media['media_url'] + ' '
    except AttributeError:
        pass

    return send

def encode_status(status):
    user = status.user
    username = html.unescape(status.user.screen_name)
    name = html.unescape(user.name) + ' (@' + username + ')'
    title = "Tweet by {0}".format(html.unescape(user.name))
    footer = str(status.created_at) + ' UTC'

    description = ''
    if twitutils.is_retweet(status):
        description += html.unescape('RT {0.user.name}: {1}'.format(twitutils.get_status(status), twitutils.get_text(status)))
    else:
        description += twitutils.get_text(status)

    print(description)

    video = twitutils.get_video(status)

    embed = discord.Embed()

    if (len(video) > 0):
        embed = discord.Embed(video=video[0], description=description, title=title)
        embed.add_field(name='Media', value=video[0])
    else:
        embed = discord.Embed(description=description, title=title)
        images = twitutils.get_images(status)
        print(images)
        if(len(images) > 0):
            embed.set_image(url=images[0])

            text = ''

            count = 0
            fields = 1
            for i in range(len(images)):
                #text +='[' + str(i + 1) + ']' + '(' + str(images[i]) + ')' + ' '
                if (len(text) < 1500 and count < 4):
                    text += make_url(str(count + 1), images[i]) + ' '
                    count += 1
                else:
                    print(len(text))
                    embed.add_field(name='Media ' + str(fields), value=text)
                    text = ''
                    count = 0
                    fields += 1

            print(len(text))
            print(text)
            if len(text) > 0:
                if fields == 1:
                    field_name = 'Media'
                else:
                    field_name = 'Media ' + str(fields)
                embed.add_field(name=field_name, value=text)

    embed.set_author(name=name, url=twitutils.make_url(username), icon_url=user.profile_image_url)
    embed.set_footer(text=footer, icon_url=user.profile_image_url)

    return embed

def make_url(text: str, url: str):
    return '[' + text + ']' '(' + url + ')'



