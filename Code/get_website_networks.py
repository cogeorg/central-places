#!/usr/bin/env python2.7
"""Generate js for website to display the network."""

import csv
import json
import pandas as pd
from string import Template

import networkx as nx
from networkx.readwrite import json_graph


def compress(d, drops):
    """Remove specified entries from sub-dict."""
    for sd in d:  # Remove enumeration and compress
        for drop in drops:
            sd.pop(drop, None)
    return d


def giant(G):
    """Return giant component of a network."""
    components = sorted(nx.connected_component_subgraphs(G),
                        key=len, reverse=True)
    return components[0]


def replace_enumeration(d, mapping):
    """Replace enumeration of node ids."""
    for sd in d:
        sd['source'] = mapping[sd['source']]
        sd['target'] = mapping[sd['target']]
    return d


if __name__ == '__main__':
    # VARIABLES
    IC = "../../InformalCollaboration/Code/"  # relative path of IC repository
    timepoints = ["early", "late"]
    ranking_folder = IC + "211_centralities/comwith_network"
    network_folder = IC + "210_network_data/comwith_network"
    positions_folder = IC + "213_node_positions"
    output_folder = "../static/js"

    # Templates
    text_tmplte = Template(
        '$name<br>'
        'Number of acknowledgements: $thanks_v (Rank: $thanks_r)<br>'
        'Betweenness centrality rank: $betw_r<br>'
        'Eigenvector centrality rank: $eig_r')
    node_tmplte = Template('{id:$id,label:"$label",title:"$title",'
                           'x:$x,y:$y,value:1,group:"$group"}')
    edge_tmplte = Template('{from:$fr,to:$to}')

    for tp in timepoints:
        # READ IN
        ranking_file = "%s/all-%s.csv" % (ranking_folder, tp)
        network_file = "%s/all-%s.gexf" % (network_folder, tp)
        positions_file = "%s/comwith_all-%s.csv" % (positions_folder, tp)
        output_file = {'graph': "%s/all-%s-network.js" % (output_folder, tp),
                       'ring': "%s/all-%s-ring.js" % (output_folder, tp)}

        with open(ranking_file, 'r') as inf:  # das hier auch noch ersetzen
            reader = csv.DictReader(inf)
            ranking_dict = {row["node"]: row for row in reader}
        pos_df = pd.read_csv(positions_file, encoding='utf-8')
        pos = {row.node: eval(row.positions) for row in pos_df.itertuples()}

        # MERGE AND REDUCE DATA
        # H is for ring view
        H = nx.read_gexf(network_file)
        id_mapping = {}  # needed to replace numeric id's in json object
        for idx, (node, data) in enumerate(H.nodes(data=True)):
            id_mapping[idx] = node
            data["occurrence"] = data.get("occurrence", 0)
        # G is for graph view
        G = giant(H)
        # remove edges representing one-time collaboration having weight < 1
        for sourc, tar, data in G.edges(data=True):
            if data["weight"] < 1 and len(data["journal"].split(';')) == 1:
                G.remove_edge(sourc, tar)
        G = nx.convert_node_labels_to_integers(G, label_attribute="name")
        # add groups, scaled positions and text
        for node, data in G.nodes(data=True):
            name = data['name']
            # Groups (compressed)
            if data["occurrence"] == 0:
                data["group"] = "a"  # pure author
            elif 'affiliation' not in data:
                data["group"] = "c"  # pure commenter
            else:
                data["group"] = "b"  # commenting author
            # Positions
            x, y = pos[name]
            data["x"] = x*10
            data["y"] = y*10
            # Text
            data['text'] = text_tmplte.substitute(
                name=name, thanks_v=data["occurrence"],
                thanks_r=ranking_dict[name]["occurrence_rank"],
                betw_r=ranking_dict[name]["betweenness_rank"],
                eig_r=ranking_dict[name]["eigenvector_rank"])

        # WRITE OUT
        # Graph view // Generate manually for vis.js's expectations
        nodes = [node_tmplte.substitute(id=node, label=data["name"],
                                        title=data['text'], x=data["x"],
                                        y=data["y"], group=data["group"])
                 for node, data in G.nodes(data=True)]
        edges = [edge_tmplte.substitute(fr=s, to=t) for s, t in G.edges()]
        out_text = u'var nodes=[{}];\nvar edges=[{}];'.format(
            ','.join(nodes), ','.join(edges))
        with open(output_file['graph'], 'w') as ouf:
            ouf.write(out_text)
        # Ring view
        ring = json_graph.node_link_data(H)
        drops = ["journal", "year", "jel", "title", "id"]
        ring['links'] = compress(ring['links'], drops)
        ring['links'] = replace_enumeration(ring['links'], id_mapping)
        r = "data = " + json.dumps(ring)  # Create real .js file
        with open(output_file['ring'], 'w') as ouf:
            ouf.write(r.encode('utf-8'))
