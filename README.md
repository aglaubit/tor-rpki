# tor-rpki

## Tor ROA Data + Graphs
Uses

**util.py**

**preprocess_consensus.py**:
- 

**graphs.py**, **graphs_all.py**, **projection.py**: 
- these files contain the analysis/graphing of the preprocessed consensus data.
- **graphs.py** requires:
  - filename: pickled consensus file annotated with ROAs: archive_pickles/year-mo-dy.pickle
  - guards: just guards (y/n)
- **graphs_all.py** uses multiple consensus


## Guard Selection Algorithm Simulation Code
To use, preprocess archived Tor consensus data with preprocess_consensus.py. Assumes that guard_sim.py + util.py are in a directory inside the directory 'rpkicoverage' and that the preprocessed consensus files are in the directory 'processed' which is also in 'rpkicoverage.'

**guard_sim.py**:
- requires these arguments:
  - start_date: the start date in year-mo-da-hr format
  - end_date: the end date in year-mo-da-hr format
  - num_clients: the number of clients to simulate
- will produce a graph of guard churn, load balance, percent of clients covered by a ROA, and percent of BW covered by a ROA

**util.py**:
- helper for guard_sim.py
- algorithm is mostly definied in the client class


## Annotate BGP RIBs with ROV Validity information
For reproducing the uncontrolled ROV experiments [here](https://github.com/RPKI/rov-measurement-code). I would not reccomend using this code.
