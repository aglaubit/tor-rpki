from datetime import datetime, timedelta
import csv
import os
import pickle
import ipaddress
import json
import requests
import urllib
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

class Relay:
    '''Relay class
    
    Attributes
    ----------
    fp : string
        Fingerprint (unique id)
    ip : string
        IP address
    ipv6 : string
        if relay has IPv6 address, ipv6 == (string) ipv6 address
        if relay doesn't have an IPv6 address, ipv6 == ''
    bw : int
        Bandwidth
    is_guard : bool
        True if has 'Guard' flag
    is_exit : bool
        True if has 'Exit' flag
    '''
    def __init__(self, fp, ip):
        # relay info
        self.fp = fp
        self.ip = ip
        self.ipv6 = ''
        self.bw = 0
        self.is_guard = False
        self.is_exit = False

        # preprocessing ROA coverage info
        self.asn = None
        self.ipv4_prefix = None
        self.ipv4_roa = None   # if roa, = [net(IPv4Network), max length(str), prefix length(str), asn]
        self.ipv6_asn = None
        self.ipv6_prefix = None
        self.ipv6_roa = None
 
        # persistently record
        self.sampled_on = datetime(1, 1, 1, 0)
        self.listed = True
        self.unlisted_since = datetime(1, 1, 1, 0)

    def __eq__(self, other):
        return self.fp == other.fp

    def __str__(self):
        return self.fp

    def __hash__(self):
        return hash(self.fp)


def datespan(s, e, delta=timedelta(hours=1)):
    '''Function to iterate through each hour in a given timespan'''
    # from https://stackoverflow.com/questions/153584/how-to-iterate-over-a-timespan-after-days-hours-weeks-and-months
    cd = s
    while cd < e:
        yield cd
        cd += delta


def get_all_ips(start_date, end_date):
    all_ipv4s = set()
    all_ipv6s = set()
    p = os.getcwd()
    path = p + '\\archive_pickles\\'
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        rs, wgd, wgg = load_consensus(path, t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H'))
        if rs:
            ipv4s = [r.ip for r in rs]
            ipv6s = [r.ipv6 for r in rs if r.ipv6 != '']
            all_ipv4s.update(ipv4s)
            all_ipv6s.update(ipv6s)    
    return all_ipv4s, all_ipv6s


def load_consensus(p, year, month, date, hour):
    '''pulls relay data from pickled file'''
    # load .pickle file
    filename = p + year + '-' + month + '-' + date + '-' + hour + '.pickle'
    try: 
        file = open(filename, 'rb')
        rs = pickle.load(file)
        wgd = pickle.load(file)
        wgg = pickle.load(file)
        return rs, wgd, wgg
    # if it doesn't exist
    except FileNotFoundError:
        print('Consensus for ' + year + '-' + month + '-' + date + '-' + hour + ' doesn\'t exist.')
        return [], 0, 0


def recent_relays_hour(year, month, date, hour):
    '''Gets relays from one consensus file (one hour)
    
    Parameters
    ----------
    year : (str) 'year'
    month : (str) 'mm'
    date : (str) 'dd'
    hour : (str) 'hr'

    Returns
    ----------
    list of Relay objects
    '''
    baseurl = 'https://collector.torproject.org/recent/relay-descriptors/consensuses/'
    url = baseurl + year + '-' + month + '-' + date + '-' + hour + '-00-00-consensus'
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')
    text = soup.get_text().split('\n')
    rs = []
    for line in text:
        # Bandwidth weights for this consensus
        if line.startswith('bandwidth-weights'):
            bw_info = line.split()
            wgd = (int(bw_info[12].split('=')[1]))  # WGD: weight for Guard+Exit-flagged nodes in guard position
            wgg = (int(bw_info[13].split('=')[1]))  # WGG: weight for Guard-flagged nodes in guard position
            break

        # relay info into Relay object
        elif line[0] == 'r' and line[1] == ' ':
            r_info = line.split('r ', 1)[1].split()
            r = Relay(r_info[1], r_info[5])  # fp and ip

        elif line[0] == 'a' and line[1] == ' ':
            a_info = line.split('a [', 1)[1].split(']', 1)[0]
            r.ipv6 = a_info

        elif line[0] == 's' and line[1] == ' ':
            s_info = line.split('s ', 1)[1].split()  # s_info : list of flags
            if all(f in s_info for f in ('Fast', 'Guard', 'Stable', 'V2Dir')):
                r.is_guard = True
            if 'Exit' in s_info:
                r.is_exit = True

        elif line[0] == 'w' and line[1] == ' ':
            bw = line.split('=')[1]  # bandwidth
            if 'Unmeasured' not in bw:
                r.bw = int(bw)
            # append relay to list
            rs.append(r)
    return relays

# faster if BGP dumps used 
def get_prefix_and_asn(ip):
    base_url = "https://stat.ripe.net/data/network-info/data.json?resource="
    url = base_url + ip
    try:
        response = urllib.request.urlopen(url).read()
    except requests.HTTPError as exception:
        print(exception) 
    data = json.loads(response)
    return data['data']['prefix'], data['data']['asns']


def get_roas(filename):
    '''get roas from csv file
    returns two lists of lists
    [ip, max length, prefix length]
    '''
    # read csv file 
    ipv4s = []
    ipv6s = []
    with open(filename, 'r') as f: 
        csvreader = csv.reader(f) 
        # skip fields
        next(csvreader) 
        # append ip to roas list
        for row in csvreader:
            try:
                ipv4 = ipaddress.IPv4Network(row[1])
                maxlen = row[2]
                prefixlen = row[1].split('/')[1]
                asn = row[0]
                ipv4s.append([ipv4, maxlen, prefixlen, asn])
            except ipaddress.AddressValueError:
                ipv6 = ipaddress.IPv6Network(row[1])
                maxlen = row[2]
                prefixlen = row[1].split('/')[1]
                asn = row[0]
                ipv6s.append([ipv6, maxlen, prefixlen, asn])
    #v4s = sorted(ipv4s, key=lambda x:x[0])
    #v6s = sorted(ipv6s, key=lambda x:x[0])
    return ipv4s, ipv6s