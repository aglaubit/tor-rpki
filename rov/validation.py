import requests
import json
import sys
import argparse
import time

def parse_arguments(args):
    parser = argparse.ArgumentParser()
    # format 2021-02: <dump-type>|<elem-type>|<record-ts>|<project>|<collector>|<router-name>|<router-ip>|<peer-ASn>|
    # <peer-IP>|<prefix>|<next-hop-IP>|<AS-path>|<origin-AS>|<communities>|<old-state>|<new-state>|<validity-state>
    parser.add_argument("data", help="BGP RIB dump")
    args = parser.parse_args(args)
    return args

'''
def add_validity_state(filename):
    #ret = []
    with open(filename, 'r') as f, open('annotated.txt', 'w') as n:
        for line in f:
            newline = line
            line = line.split('|')
            if len(line) < 11:
                continue
            pre = line[9].rstrip()
            asn = line[12].rstrip()
            url = "http://[my ip address]:8323/api/v1/validity/" + asn + "/" + pre
            r = requests.get(url)
            if r.status_code == 400:
                print('Bad Request')
                continue
            data = r.json()
            if data['validated_route']['validity']['state'] == "not-found":
                newline += "|1\n"
                n.write(newline)
            elif data['validated_route']['validity']['state'] == "valid":
                newline += "|0\n"
                n.write(newline)
            elif data['validated_route']['validity']['state'] == "invalid":
                if data['validated_route']['validity']['reason'] == 'as':
                    newline += "|3\n"
                    n.write(newline)
                elif data['validated_route']['validity']['reason'] == 'length':
                    newline += "|4\n"
                    n.write(newline)
                else:
                    print(data['validated_route']['validity']['reason'])
                    newline += "|5\n"
                    n.write(newline)
            else:
                print(data['validated_route']['validity']['state'])
                val = input('Annotate with?')
                newline += val
                newline += '\n'
            #ret.append(newline)
    #return ret
'''

def add_validity_state(asn_pre):
    ret = set()
    for ap in asn_pre:
        ap = ap.split('|')
        asn = ap[0]
        pre = ap[1]
        url = "http://[ip address]:8323/api/v1/validity/" + asn + "/" + pre
        r = requests.get(url)
        if r.status_code == 400:
            print('Bad Request: ' + asn + ' ' + pre)
            validity = '1'
        else:
            data = r.json()
            if data['validated_route']['validity']['state'] == "not-found":
                validity = '1'
            elif data['validated_route']['validity']['state'] == "valid":
                validity = '0'
            elif data['validated_route']['validity']['state'] == "invalid":
                if data['validated_route']['validity']['reason'] == 'as':
                    validity = '3'
                elif data['validated_route']['validity']['reason'] == 'length':
                    validity = '4'
            else:
                print(data['validated_route']['validity']['state'])
                val = input('Annotate with?')
                validity = val
        ret_val = asn + '|' + pre + '|' + validity + '\n'
        ret.add(ret_val)
    return ret


def write_to_new_file(new_lines, filename):
    with open(filename, 'w') as f2:
        for line in new_lines:
            f2.write(line)


def preprocess(filename):
    unique = set()
    with open(filename, 'r') as f:
        for line in f:
            line = line.split('|')
            if len(line) < 11:
                print('Bad Record')
                continue
            pre = line[9].rstrip()
            asn = line[12].strip(' }{')
            if ',' in asn:
                asn = asn.split(',')
                for a in asn:
                    a = a.strip()
                    ap = a + '|' + pre
                    unique.add(ap)
                continue
            ap = asn + '|' + pre
            unique.add(ap)
    return unique

def main(args):
    start_time = time.time()
    args = parse_arguments(args)
    small = preprocess(args.data)
    print("--- %s seconds to preprocess ---" % (time.time() - start_time))
    new = add_validity_state(small)
    print("--- %s seconds to validate ---" % (time.time() - start_time))
    write_to_new_file(new, 'rrc00_04_annotated.txt')
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
