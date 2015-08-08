# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib
import urllib2
import re

from copy import deepcopy
from lxml import etree
from time import sleep
from termcolor import colored

FILENAME_URL_XPATH = '//*[@id="code_search_results"]/div[1]/div/p/a[2]/@href'

regex = r'^([\w-]*)(?:(>=|>|==|<=|<)([\d\.]*)(?:,(>=|>|==|<=|<)([\d\.]*))?)?'
pattern = re.compile(regex, re.M)


def parse_requirements(requirements):
    entries = pattern.findall(requirements.lower())
    return [
        {'status': None, 'entry': entry}
        for entry in entries
        if entry != ('', '', '', '', '')
    ]


def query_builder(requirements=None, repos=None):
    q = 'filename:requirements.txt'

    for entry in parse_requirements("\n".join(requirements)):
        q += ' "{}"'.format(entry['entry'][0])

    for repo in repos or []:
        q += ' repo:{}'.format(repo)

    return q


def get_repo_from_blob(filename_blob_url):
    return 'http://github.com/' + '/'.join(filename_blob_url.split('/')[1:3])


def get_raw_file_url_from_blob(filename_blob_url):
    return 'https://raw.githubusercontent.com' + \
           filename_blob_url.replace('/blob/', '/')


def is_similar(requirements_parsed, repo_entries_parsed):
    for entry in requirements_parsed:

        repo_entries_to_check = [
            e for e in repo_entries_parsed if not e['status']
        ]

        for repo_entry in repo_entries_to_check:

            if entry['entry'] == repo_entry['entry']:
                entry['status'] = repo_entry['status'] = 'OK'

                break

            if entry['entry'][0] == repo_entry['entry'][0]:
                entry['status'] = repo_entry['status'] = 'ALMOST'
                break

        if not entry['status']:
            return False

    return True


def main(requirements_parsed):

    page = 1
    params = {
        'type': 'Code',
        # 'utf8': '✓',requirements_raw_file
        'ref': 'searchresults',
        'q': query_builder(requirements),
    }

    while True:
        params['p'] = str(page)
        url = 'https://github.com/search?' + urllib.urlencode(params)
        # print url

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        # print ">>  PAGE: %d <<" % page
        try:
            response = opener.open(url)
        except Exception as e:
            # print str(e)
            print "Github has to rest for a minute, please be patient ;)"
            sleep(70)
            response = opener.open(url)

        tree = etree.parse(response, etree.HTMLParser())

        filename_blob_urls = tree.xpath(FILENAME_URL_XPATH)

        if not filename_blob_urls:
            break

        for filename_blob_url in filename_blob_urls:
            # print "Repo" + '/'.join(filename_blob_url.split('/')[1:3])
            filename_path = '/'.join(filename_blob_url.split('/')[5:])

            if 'requirements' in filename_path:
                raw_file_url = get_raw_file_url_from_blob(filename_blob_url)
                response = opener.open(raw_file_url)
                try:
                    file_content = response.read()
                except:
                    print "there was some problem..."

                requirements_parsed_cpy = deepcopy(requirements_parsed)
                repo_entries_parsed = deepcopy(parse_requirements(file_content))

                result = is_similar(requirements_parsed_cpy, repo_entries_parsed)

                if result:
                    print "Repository: " + get_repo_from_blob(filename_blob_url)

                    repo_status = [
                        entry['status'] == 'OK'
                        for entry in requirements_parsed_cpy
                    ]

                    if all(repo_status):
                        print "Status:" + colored("Perfect match", 'green')
                    else:
                        print "Status:" + colored("Similar project", 'yellow')

                    print "File: " + filename_path

                    for entry in repo_entries_parsed:
                        print "   ",
                        if entry['status'] == 'OK':
                            print colored("".join(entry['entry']), 'green')
                        elif entry['status'] == 'ALMOST':
                            print colored(
                                entry['entry'][0], 'cyan'
                            ) + "".join(entry['entry'][1:])
                        else:
                            print "".join(entry['entry'])

                    print ""

        page += 1

if __name__ == "__main__":

    requirements = [
        "django==1.8",
        "djangorestframework==3.1.1",
        "django-haystack"
    ]

    requirements_parsed = parse_requirements('\n'.join(requirements))

    main(requirements_parsed)
