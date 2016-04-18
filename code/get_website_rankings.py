#!/usr/bin/env python2.7
"""Generate html for website to display the network rankings."""

import csv
from collections import OrderedDict
from itertools import product
from string import Template


def get_aff(aff_list):
    """Return unique affiliation(s) from pandas series."""
    a = [aff for aff in aff_list if aff != '']
    if len(a) > 0:
        return "; ".join(set(a))
    else:
        return ""


def get_linktext(node, nw, tp):
    """"Return string with link depending on network definition."""
    if nw == "comwith":
        t = Template("<a href=\"{{url_for('rings',time='$tp',"
                     "focus='$link')}}\">$text</a>")
        return t.substitute(tp=tp, text=node,
                            link=node.replace(" ", "_").replace("'", ""))
    else:
        return node

def get_ranking_html(rank_dct, nw, tp, measure):
    """Return html for ranking list."""
    header = """
<thead>
    <tr>
        <th>Rank</th>
        <th>Name</th>
        <th>Affiliation (on published papers)</th>
        <th>Value</th>
    </tr>
</thead>
<tbody>
"""
    t = Template('<td>$rank</td><td>$text</td><td>$aff</td><td>$val</td>')
    table = []
    for node, sub in rank_dct.items():
        # Get elements
        rank = sub[measure + '_rank']
        text = get_linktext(node, nw, tp)
        aff = sub["affiliation"][tp]
        value = round_if_needed(rank_dct[node][measure], measure)
        # Combine elements
        entry = t.substitute(rank=rank, text=text, aff=aff, val=value)
        table.append('<tr>' + entry + '</tr>')
    return header + '\n'.join(table) + "\n</tbody>"


def round_if_needed(num, meas):
    """Return value with precision depending on measure."""
    if meas == "occurrence":
        return int(num)
    else:
        return round(float(num), 4)



if __name__ == '__main__':
    # VARIABLES
    IC = "../../InformalCollaboration/Code/"  # relative path of IC repository
    networks = ["comwith", "auth"]
    input_folder = IC + "211_centralities/"
    affiliation_file = IC + "112_node_lists/all-all_authors.csv"
    output_folder = "../templates/rankings/"

    year_map = {"early": range(1998, 2000+1),
                "late": range(2009, 2011+1)}
    timepoints = year_map.keys()

    combs = product(timepoints, networks)
    for (tp, nw) in combs:
        input_file = input_folder + nw + "_network/all-" + tp + ".csv"

        keeps = ["node", "occurrence", "betweenness", "eigenvector"]

        # READ IN
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            ranks = {row.pop("node"): row for row in reader}
        with open(affiliation_file, 'r') as f:
            reader = csv.DictReader(f)
            affs = {row.pop("author"): row for row in reader}
        # Remove unneccessary information; merge affiliations
        for author, subdict in ranks.items():
            for key in subdict.keys():
                if not any(variable in key for variable in keeps):
                    del subdict[key]
            subdict["affiliation"] = d = dict.fromkeys(timepoints, "")
            if author in affs:
                for tp, years in year_map.items():
                    cur_affs = [affs[author][str(y)] for y in year_map[tp]]
                    d.update({tp: get_aff(cur_affs)})

        # SORT AND WRITE OUT
        for measure in keeps[1:]:
            reduced_dict = {key: subdict for key, subdict in ranks.items()
                            if subdict[measure + '_rank'] != ""}
            od = OrderedDict(sorted(reduced_dict.iteritems(),
                             key=lambda kv: int(kv[1][measure + '_rank'])))

            out_text = get_ranking_html(od, nw, tp, measure)
            output_file = '{}all-{}_{}_{}.html'.format(output_folder, nw,
                                                       tp, measure)
            with open(output_file, 'w') as ouf:
                ouf.write(out_text)
