# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib
import urllib2
from lxml import etree
from time import sleep
from github import Github


github = Github()

def query_builder(requirenments=None, repos=None):
    q = 'filename:requirenments.txt'
    for entry in requirenments or []:
        package, version = entry.split('==')
        q += ' "{}"'.format(package)

    for repo in repos or []:
        q += ' repo:{}'.format(repo)

    return q

requirenments = [
    "django==1.8",
    "django-rest-framework==3.1.1",
]

query = query_builder(requirenments)

page = 1
params = {
    'type': 'Code',
    # 'utf8': '✓',
    'ref': 'searchresults',
    'q': query,
}


repositories = []

while True:
    params['p'] = str(page)
    url = 'https://github.com/search?' + urllib.urlencode(params)

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    print ">>  PAGE: %d <<" % page
    try:
        response = opener.open(url)
    except urllib2.HTTPError, e:
        print str(e)
        sleep(70)
        response = opener.open(url)

    tree = etree.parse(response, etree.HTMLParser())
    xpath_selector1 = '//*[@id="code_search_results"]/div[1]/div/p/a[1]'
    elements = tree.xpath(xpath_selector1)

    if not elements:
        break

    repos = [elem.text for elem in elements]

    repositories += repos

    api_query = query_builder(requirenments, repos)
    results = github.search_code(api_query)
    for result in results:
        requirenments_path = result.html_url
        raw_requirenments = requirenments_path.replace('https://github.com/', 'https://raw.githubusercontent.com/').replace('/blob/', '/')

        print raw_requirenments
        response = opener.open(raw_requirenments)
        print response.read()


    page += 1





# from lxml.etree import tostring
#
# # url = "https://github.com/search?p=2&q=filename%3Arequirements.txt+%22Django%22+%22django-rest-framework%22&ref=searchresults&type=Code&utf8=%E2%9C%93"
# url = "https://github.com/search?p=2&utf8=%E2%9C%93&q=filename%3Arequirements.txt+%22Django%22+%22django-rest-framework%22+%22django-haystack%22+%22pysolr%22&type=Code&ref=searchresults"
#
#
#
# results =
# print str(results)
#
#
for result in results:
    requirenments_path = result.html_url
    raw_requirenments = requirenments_path.replace('https://github.com/', 'https://raw.githubusercontent.com/').replace('/blob/', '/')

    print raw_requirenments
#
# print "by"