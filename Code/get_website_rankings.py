#!/usr/bin/env python2.7
"""Generate html for website to display the network rankings."""

import csv
from collections import OrderedDict
from itertools import product
from string import Template


def get_linktext(node, nw, tp):
    """"Return string with link depending on network definition."""
    if nw == "comwith":
        t = Template("<a href=\"{{url_for('rings',time='$tp',"
                     "focus='$link')}}\">$text</a>")
        return t.substitute(tp=tp, text=node,
                            link=node.replace(" ", "_").replace("'", ""))
    else:
        return node


def round_if_needed(num, meas):
    """Return value with precision depending on measure."""
    if meas == "occurrence":
        return int(num)
    else:
        return round(float(num), 4)


def write_out_ranking(rank_dct, file, nw, tp, measure):
    """Write out html file for ranking list."""
    header = """
<thead>
    <tr>
        <th>Rank</th>
        <th>Name</th>
        <th>Affiliation (in 2011, if in data)</th>
        <th>Value</th>
    </tr>
</thead>
<tbody>
"""
    table = []
    for node, sub in rank_dct.items():
        # Get elements
        rank = sub[measure + '_rank']
        text = get_linktext(node, nw, tp)
        aff = sub["affiliation"]
        value = round_if_needed(rank_dct[node][measure], measure)
        # Combine elements
        t = Template('<td>$rank</td><td>$text</td><td>$aff</td><td>$val</td>')
        entry = t.substitute(rank=rank, text=text, aff=aff, val=value)
        table.append('<tr>' + entry + '</tr>')
    out_text = header + '\n'.join(table) + "\n</tbody>"
    with open(output_file, 'w') as ouf:
        ouf.write(out_text)


if __name__ == '__main__':
    # VARIABLES
    IC = "../../InformalCollaboration/Code/"  # relative path of IC repository
    timepoints = ["early", "late"]
    networks = ["comwith", "auth"]
    input_folder = IC + "211_centralities/"
    affiliation_file = IC + "112_node_lists/all-all_authors.csv"
    output_folder = "../templates/rankings/"

    combs = product(timepoints, networks)
    for (tp, nw) in combs:
        input_file = input_folder + nw + "_network/all-" + tp + ".csv"

        keeps = ["node", "occurrence", "betweenness", "eigenvector"]

        # READ IN
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            ranks = {row["node"]: row for row in reader}
        with open(affiliation_file, 'r') as f:
            reader = csv.DictReader(f)
            affs = {row["author"]: row["2011"] for row in reader}
        # Remove unneccessary information; merge affiliations
        for author, subdict in ranks.items():
            for key in subdict.keys():
                if not any(variable in key for variable in keeps):
                    del subdict[key]
            if author in affs:
                subdict["affiliation"] = affs[author]
            else:
                subdict["affiliation"] = ""

        # SORT AND WRITE OUT
        for measure in keeps[1:]:
            reduced_dict = {key: subdict for key, subdict in ranks.items()
                            if subdict[measure + '_rank'] != ""}
            od = OrderedDict(sorted(reduced_dict.iteritems(),
                             key=lambda kv: int(kv[1][measure + '_rank'])))

            output_file = '{}all-{}_{}_{}.html'.format(output_folder, nw,
                                                       tp, measure)
            write_out_ranking(od, output_file, nw, tp, measure)
