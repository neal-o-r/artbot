# vim: set sts=4 ts=4 sw=4 expandtab:

import requests
import settings
import shutil
import json


def parse_style_painting(resp):
    '''
    input : STYLE request response
    output: dictionary of relevant fields

        gets relevant fields from painting JSON
        annoyingly they use different formats images by style
        and by artist, this function only works on styles
    '''
    d = dict(url = resp['image'],
            title = resp['title'],
            artist = resp['artistName'],
            year = resp['year'])

    return d

def parse_artist_painting(resp):
    '''
    input : ARTIST request response
    output: dictionary of relevant fields

        gets relevant fields from painting JSON
        annoyingly they use different formats images by style
        and by artist, this function only works on artists
    '''
    d = dict(url = ''.join(resp['image'].split('!')[:-1]),
            title = resp['title'],
            artist = resp['artistName'],
            year = resp['completitionYear'])

    return d


def images_by_style(style='kitsch', to_page=10):

    images = []
    for i in range(1, to_page):
        url = settings.base_url + settings.style_url(style) + \
                                "&" + settings.pagination_style + str(i)
        try:
            response = requests.get(url, timeout=settings.metadata_timeout)
            images.extend(list(map(parse_style_painting,
                            response.json()['Paintings'])))

        except requests.exceptions.RequestException as e:
            print(e)
            break

    return images


def images_by_artist(name='Francis Bacon'):

    all_artists = json.load(open('artists.json', 'r'))
    assert name in [a['artistName'] for a in all_artists]

    artist = [a for a in all_artists if a['artistName'] == name][0]

    url = settings.app_url + 'Painting/PaintingsByArtist'
    params = {'artistUrl': artist['url'], 'json':2}

    response = requests.get(url, params=params,
                    timeout=settings.metadata_timeout)

    images = list(map(parse_artist_painting, response.json()))
    return images


def dump_metadata(images):
    with open(settings.save_location + 'metadata.json', 'w') as f:
        json.dump(images, f, sort_keys=True, indent=4)


def download(images):

    downloaded_images = []
    for img in images:
        try:
            response = requests.get(img['url'],
                                timeout=settings.metadata_timeout, stream=True)
        except requests.exceptions.RequestException as e:
            print(e)
            break

        image_name = f"{img['title']}-{img['artist']}-{img['year']}.jpg"
        file_location = settings.save_location + image_name

        with open(str(file_location), 'wb') as outfile:
                shutil.copyfileobj(response.raw, outfile)

        downloaded_images.append(img)

    dump_metadata(downloaded_images)


if __name__ == '__main__':

    images = images_by_artist()
    download(images[:1])
