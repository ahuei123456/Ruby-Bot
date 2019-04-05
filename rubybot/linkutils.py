import tweepy, html, urllib.request, os, requests, bs4, re
from os import path

cdj_url = path.join(r'http://www.cdjapan.co.jp/aff/click.cgi/PytJTGW7Lok/5794/A596200/product%2F')


def get_link(link: str):
    print(link)
    links = []
    if link.find('instagram.com') != -1:
        links.append(get_insta(link))
    elif link.find('ameblo.jp') != -1:
        links.extend(get_ameblo(link))
    elif link.find('lineblog.me') != -1:
        links.extend(get_lineblog(link))
    print(links)
    return links


def get_ameblo(ameblo_link: str):
    r = requests.get(ameblo_link)
    html = r.content
    soup = bs4.BeautifulSoup(html, 'html.parser')

    food = soup.find_all('a')

    links = list()
    for item in food:
        try:
            if 'detailOn' in item['class']:
                for child in item.children:
                    image = child['src'].split('?')[0]
                    #image = image.sub('', 't\d*_')
                    links.append(image)
        except KeyError:
            pass

    return links


def get_insta(insta_link: str):
    r = requests.get(insta_link)
    html = r.content
    soup = bs4.BeautifulSoup(html, 'html.parser')
    food = soup.find_all('meta')
    link = ''
    for item in food:
        try:
            if item['property'] == 'og:image':
                link = item['content']
                link = link.split('?ig_cache_key')[0]
            if item['property'] == 'og:video':
                link = item['content']
        except AttributeError:
            pass
        except KeyError:
            pass

    return link


def get_lineblog(lineblog_link: str):
    r = requests.get(lineblog_link)
    html = r.content
    soup = bs4.BeautifulSoup(html, 'html.parser')

    food = soup.find_all('a')

    links = list()
    for item in food:
        try:
            if '_blank' in item['target']:
                image = item['href']
                if 'obs.line-scdn.net' in image:
                    links.append(image)
        except KeyError:
            pass

    return links


def get_twitter(twitter_link: str):
    r = requests.get(twitter_link)
    html = r.content
    soup = bs4.BeautifulSoup(html, 'html.parser')

    food = soup.find_all('div')

    links = list()
    for item in food:
        try:
            if 'AdaptiveMedia-photoContainer js-adaptive-photo ' in item['class']:
                image = item['data-image-url'] + ':orig'
                links.append(image)
        except KeyError:
            pass

    return links


def shill(code: str):
    codes = code.split(r'/')
    code = codes[len(codes) - 1]

    return cdj_url + code

def get_cdjapan(cdj_link: str):
    r = requests.get(cdj_link)
    html = r.content
    soup = bs4.BeautifulSoup(html, 'html.parser')

    food = soup.find_all('div')
    data = dict()
    for item in food:
        try:
            if 'product_info' in item['class']:
                for child in item.children:
                    print(child)
        except KeyError:
            pass
    pass