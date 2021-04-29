import requests
import json
import sys
import argparse
import time

def parse_arguments(args):
    parser = argparse.ArgumentParser()
    # format: <dump-type>|<elem-type>|<record-ts>|<project>|<collector>|<router-name>|<router-ip>|<peer-ASn>|
    # <peer-IP>|<prefix>|<next-hop-IP>|<AS-path>|<origin-AS>|<communities>|<old-state>|<new-state>|<validity-state>
    parser.add_argument("data", help="BGP RIB dump")
    # format: <origin-AS>|<prefix>|<validity state>
    parser.add_argument("annotated", help="annotated BGP RIB dump without duplicates")
    args = parser.parse_args(args)    
    return args


def make_validation_dict(filename):
    validation = dict()
    with open(filename, 'r') as f:
        for line in f:
            line = line.split('|')
            asn = line[0]
            pre = line[1]
            validity_state = line[2]
            asn_pre = asn + '|' + pre
            validation.setdefault(asn_pre, validity_state)
    return validation


def annotate_validity_state(filename, validation):
    with open(filename, 'r') as f, open('annotated2.txt', 'w') as n:
        for line in f:
            newline = line.rstrip()
            line = line.split('|')
            if len(line) < 11:
                continue
            pre = line[9].rstrip()
            asn = line[12].strip(' }{')
            if ',' in asn:
                asn = asn.split(',')
                vss = []
                for a in asn:
                    a = a.strip()
                    asn_pre = a + '|' + pre
                    vs = validation[asn_pre].rstrip()
                    vss.append(vs)
                if '0' in vss:
                    validity_state = '0'
                else:
                    validity_state = vss[-1]
            else:
                asn_pre = asn + '|' + pre
                validity_state = validation[asn_pre].rstrip()
            newline += '|' + validity_state + '\n'
            n.write(newline)


def main(args):
    start_time = time.time()
    args = parse_arguments(args)
    validation = make_validation_dict(args.annotated)
    print("--- %s seconds to process validity states ---" % (time.time() - start_time))
    new = annotate_validity_state(args.data, validation)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))