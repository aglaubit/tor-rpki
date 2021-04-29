# tor-rpki

## Tor ROA Data + Graphs
Uses archived Tor consensus data ([link](https://collector.torproject.org/archive/relay-descriptors/consensuses/)), ROA data ([link](https://rpki-validator.ripe.net/roas)), and network info queried from the RIPEstat Data API ([link](https://stat.ripe.net/data/network-info/data.json?resource=)).

**util.py**:
- helper for preprocess_consensus.py

**preprocess_consensus.py**:
- requires these arguments:
  - start_date: date in year-mo-da-hr format
  - end_date: date in year-mo-da-hr format (not inclusive)
  - roas: csv file of validated ROAS ([downloaded here](https://rpki-validator.ripe.net/roas))
- pickle_consensus(start_date, end_date): pickles consensus data in the range and returns a set of all IPv4 addresses and a set of all IPv6 addresses
  - places these intermediate consensus pickles in directory 'archive_pickles'
- get_pre_asn(all_ipv4s, all_ipv6s): gets the prefix and ASN for each relay using get_prefix_and_asn(ip) (defined in util)
  - returns dict (ip -> [prefix, asn])
- coverage_dict(args.roa, all_ipv4s, all_ipv6s): uses csv file of ROAs
  - returns dict (ip -> [ip, maxlength, prefixlength, asn]) (value is the ROA (or None if no ROA))
  - only takes one set of ROAs, so will process consensuses from the start date to the end date with the same RPKI data
- update_consensus_pickle(start_date, end_date, ipv4_covg, ipv6_covg, ipv4_asns, ipv6_asns): uses coverage dicts and prefix/asn dicts to update consensus pickles with ROA coverage
  - requires a directory called processed where the preprocessed consensus pickles will be placed

**graphs.py**, **graphs_all.py**, **projection.py**: 
- these files contain the analysis/graphing of the preprocessed consensus data (they're a little redundant/overlapping)
- **graphs.py** requires:
  - filename: pickled consensus file annotated with ROAs
  - guards: just guards (y/n)
- **graphs_all.py** uses multiple consensuses for a temporal analysis
- **projection.py** uses multiple consensuses and has functions for getting coverage data split across relay AS


## (Sim) Guard Selection Algorithm Simulation Code
To use, preprocess archived Tor consensus data with preprocess_consensus.py. Assumes that guard_sim.py + util.py are in a directory inside the directory 'rpkicoverage' and that the preprocessed consensus files are in the directory 'processed' which is also in 'rpkicoverage.'

**guard_sim.py**:
- requires these arguments:
  - start_date: the start date in year-mo-da-hr format
  - end_date: the end date in year-mo-da-hr format
  - num_clients: the number of clients to simulate
- will produce a graph of guard churn, load balance, percent of clients covered by a ROA, and percent of network BW covered by a ROA

**util.py**:
- helper for guard_sim.py
- algorithm is mostly definied in the client class


## (ROV) Annotate BGP RIBs with ROV Validity information
These scripts annotate BGP RIB files with RPKI data for reproducing the uncontrolled ROV experiments [here](https://github.com/RPKI/rov-measurement-code). I would not reccomend using this code, as it would be a lot simpler to use a set of VRPs to manually check each BGP announcement to see if 1. it's covered by a ROA 2. if the ROA matches the announcement.
