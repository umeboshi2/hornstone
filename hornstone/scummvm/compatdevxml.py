import os
import xml.etree.ElementTree as ET
import csv

import requests

scummvm_compat_xml_url = 'https://github.com/scummvm/scummvm-web/raw/master/data/compatibility/compat-DEV.xml'  # noqa


def get_scummvm_compat_xml_remote(url):
    response = requests.get(url)
    if not response.ok:
        raise RuntimeError("request returned %s" % response)
    return response.content


def get_scummvm_compat_xml(url):
    filename = 'compat-DEV.xml'
    if not os.path.isfile(filename):
        content = get_scummvm_compat_xml_remote(url)
        with open(filename, 'w') as outfile:
            outfile.write(content)
    else:
        print("%s exists." % filename)


def get_one_element(element, tagname):
    elements = element.findall(tagname)
    if len(elements) != 1:
        msg = "Unable to get one element %s with tag %s"
        raise RuntimeError(msg % (element, tagname))
    return elements[0]


def parse_game_element(element):
    data = dict()
    for key in ['name', 'target', 'support_level', 'notes']:
        data[key] = get_one_element(element, key).text.strip()
    return data


def parse_company_tag(element, gdict):
    name_el = get_one_element(element, 'name')
    company = name_el.text
    if company in gdict:
        raise RuntimeError("Company %s already in dictionary" % company)
    gdict[company] = dict()
    games_el = get_one_element(element, 'games')
    for el in games_el:
        data = parse_game_element(el)
        target = data['target']
        if target in gdict[company]:
            raise RuntimeError("Duplicate target %s" % target)
        gdict[company][data['target']] = data


def make_target_data(filename):
    games = dict()
    tree = ET.parse(filename)
    root = tree.getroot()
    for child in root:
        if child.tag == 'company':
            parse_company_tag(child, games)
    targets = dict()
    for company in games:
        for target in games[company]:
            if target in targets:
                raise RuntimeError("Already processed target %s" % target)
            targets[target] = games[company][target]
            targets[target]['company'] = company
    return targets


def make_target_csv(targets):
    filename = 'targets.csv'
    if os.path.isfile(filename):
        return
    keys = list(targets.keys())
    print("Targets", len(keys))
    keys.sort()
    fields = ['target', 'name', 'company', 'support_level', 'notes']
    with open(filename, 'w') as outfile:
        writer = csv.DictWriter(outfile,
                                fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for key in keys:
            writer.writerow(targets[key])
            print(targets[key])
