import requests

URL_API = 'https://scrapbox.io/api/pages'


def getDescriptions(projectName, pageTitle):
    URL = f'{URL_API}/{projectName}/{pageTitle}/text'
    res = requests.get(URL)
    return res.text.split('\n')[1:]
