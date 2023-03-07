sd_graph is a utility to be used in conjunction with Bill Ackerman's
"sd, A Square Dance Caller's Helper" (see
http://www.challengedance.org/sd/sd_doc.pdf).

sd, and sdtty, are two different user interfaces for an application
that allows a square dance caller to develop sequences of calls and
see the resulting positions of the dancers.  When creating a sequence,
be sure that "keep all pictures" is enabled so that the output file
will include the formation diagrams.

sd_graph reads a sequence file as written by sd, and produces a graph
with square dance formations as nodes and square dance calls as edges.
In the output_directory it writes an svg file for each unique
formation that appears in the sequence file, a GraphViz dot file for
the resulting graph, an svg rendering of that graph, and a
graph.pickle file that accumulates all of the nodes and edges for any
sequence file that has been processed with respect to this
output_directory.

The example directory includes sequence files for "chicken plucker"
and some variations on it.  These can be processed with the commands

<pre>
python3 sd_graph.py -output-directory=example example/plain_chicken_plucker.txt

python3 sd_graph.py -output-directory=example example/half_chicken_plucker.txt

python3 sd_graph.py -output-directory=example example/variations1.txt

python3 sd_graph.py -output-directory=example example/variations2.txt

python3 sd_graph.py -output-directory=example example/dixie_grand.txt

python3 sd_graph.py -output-directory=example example/swing_thru.txt
</pre>

After each command you can view graph.svg in a web browser to see the
graph.

The file
[basic_chicken_plucker.svg](https://raw.githubusercontent.com/MarkNahabedian/SquareDanceFormationDiagrams/master/sd_graph/example/basic_chicken_plucker.svg?sanitize=true)
is the graph after the first two
commands were run.  all.svg is a graph of all four sequence files.

You can specify multiple input files in a single command.

[example/ChickenPluckerall.svg](https://raw.githubusercontent.com/MarkNahabedian/SquareDanceFormationDiagrams/master/sd_graph/example/ChickenPlucker/all.svg?sanitize=true)
is the diagram after all five files are processed.
