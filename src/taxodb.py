#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Corinne Maufrais
# Institut Pasteur, DSI/CIB
# maufrais@pasteur.fr
#
# version 2

import sys
import argparse
from bsddb import db                   # the Berkeley db data base


def extract_LI_and_OC(nodes, taxid):
    li = ''  # list of parent taxid
    oc = ''
    while taxid in nodes and taxid != '1':
        if nodes[taxid]['id_parent'] != '1':
            li = nodes[taxid]['id_parent'] + '; ' + li
        if nodes[taxid]['id_parent'] == taxid:
            taxid = '1'
        else:
            taxid = nodes[taxid]['id_parent']
            if taxid != '1':
                if nodes[taxid]['rank'] != 'no rank':
                    oc = "%s (%s); %s" % (extract_OS(nodes, taxid), nodes[taxid]['rank'], oc)
                else:
                    oc = "%s; %s" % (extract_OS(nodes, taxid), oc)
    return li, oc


def extract_OS(nodes, taxid):
    if 'scientific name' in nodes[taxid]['names']:
        return nodes[taxid]['names']['scientific name'][0]  # 80 car
    elif 'equivalent name' in nodes[taxid]['names']:
        return nodes[taxid]['names']['equivalent name'][0]
    elif 'synonym' in nodes[taxid]['names']:
        return nodes[taxid]['names']['synonym'][0]
    elif 'authority' in nodes[taxid]['names']:
        return nodes[taxid]['names']['authority'][0]
    elif 'common name' in nodes[taxid]['names']:
        return nodes[taxid]['names']['common name'][0]
    else:
        return nodes[taxid]['names'].keys()[0][0]


def print_line(outfh, line, tag, car=80):
    i = 0
    while i < len(line):
        st = line[i:i+car-5]
        if st[-1] in (';', ' ', '\n'):
            print >>outfh, '%s   %s' % (tag, st.strip())
        else:
            while st[-1] not in (';', ' '):
                st = st[:-1]
                i -= 1
            print >>outfh, '%s   %s' % (tag, st.strip())
        i += car - 5


def flat_db_creation(taxodbfh, nodes, taxid, car=80):
    li, OC = extract_LI_and_OC(nodes, taxid)
    print >>taxodbfh, 'ID   %s;' % taxid
    print >>taxodbfh, 'XX'
    print_line(taxodbfh, li, 'LI', car)
    print >>taxodbfh, 'XX'
    OS = extract_OS(nodes, taxid)
    print >>taxodbfh, 'OS   %s;' % OS
    print_line(taxodbfh, OC, 'OC', car)
    print >>taxodbfh, '//'


def table_ceation(os_vs_oc_fh, nodes, taxid):
    li, OC = extract_LI_and_OC(nodes, taxid)
    for LOS in nodes[taxid]['names'].values():
        for OS in LOS:
            print >>os_vs_oc_fh, '%s\t %s' % (OS, OC)


def bdb_creation(os_vs_oc_bdb, nodes, taxid):
    li, OC = extract_LI_and_OC(nodes, taxid)
    for LOS in nodes[taxid]['names'].values():
        for OS in LOS:
            os_vs_oc_bdb.put(OS, OC)


def parse_nodes(nodesfh):
    nodes = {}
    good_tax_ids = []

    line = nodesfh.readline()
    while line:
        fld = line[:-1].split('\t|\t')
        if fld[0] in nodes:
            print >>sys.stderr, "WARNING: Duplicate tax_id: %s" % fld[0]
        else:
            # name == {'name class': 'OS'} ex: {'scientific name': 'Theileria parva.'}
            nodes[fld[0]] = {'id_parent': fld[1], 'rank': fld[2], 'names': {}}
            if (fld[2] == 'species' or fld[2] == 'no rank' or fld[2] == 'subspecies') and fld[0] != '1':
                good_tax_ids.append(fld[0])
        line = nodesfh.readline()
    return nodes, good_tax_ids


def parse_names(namesfh, nodes):
    line = namesfh.readline()
    while line:
        fld = line[:-3].split('\t|\t')
        if fld[0] in nodes:
            if fld[3] in nodes[fld[0]]['names']:
                nodes[fld[0]]['names'][fld[3]].append(fld[1])  # use scientific name if exist
            else:
                nodes[fld[0]]['names'][fld[3]] = [fld[1]]
        else:
            print >>sys.stderr, "WARNING: No corresponding tax_id: %s" % fld[0]
        line = namesfh.readline()
    return nodes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='taxodb.py',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="")

    general_options = parser.add_argument_group(title="Options", description=None)

    general_options.add_argument("-n", "--names", dest="namesfh",
                                 help="names.dmp from NCBI taxonomy databank",
                                 metavar="file",
                                 type=file,
                                 required=True)
    general_options.add_argument("-d", "--nodes",
                                 action='store',
                                 dest='nodesfh',
                                 metavar="file",
                                 type=file,
                                 help='nodes.dmp from NCBI taxonomy databank',
                                 required=True)
    general_options.add_argument("-k", "--flatdb",
                                 dest="taxodbfh",
                                 help="Output file: flat databank format.",
                                 metavar="File",
                                 type=argparse.FileType('w'),
                                 default='taxodb')
    general_options.add_argument("-t", "--tab",
                                 dest="os_vs_oc_fh",
                                 help="Output file: tabulated format. Organism with classification.",
                                 metavar="File",
                                 type=argparse.FileType('w'),
                                 default='taxodb_osVSoc.txt',)
    general_options.add_argument("-b", "--bdb",
                                 dest="os_vs_oc",
                                 help="Output file: Berleley db format",
                                 metavar="File",
                                 default='taxodb.bdb',)

    args = parser.parse_args()

    # ####### TO DO
    #    format verification: names.dmp and nodes.dmp
    # ##########

    nodes, good_tax_ids = parse_nodes(args.nodesfh)
    nodes = parse_names(args.namesfh, nodes)

    # ## Remarks: args.taxodbfh and args.os_vs_oc must be dissociated for dbmaint administration

    if args.taxodbfh:
        for taxid in good_tax_ids:
            flat_db_creation(args.taxodbfh, nodes, taxid)

    if args.os_vs_oc_fh:
        for taxid in good_tax_ids:
            table_ceation(args.os_vs_oc_fh, nodes, taxid)

    if args.os_vs_oc:
        # Get an instance of BerkeleyDB
        os_vs_oc_bdb = db.DB()
        # Create a database in file "osVSocDB" with a Hash access method
        #       There are also, B+tree and Recno access methods
        os_vs_oc_bdb.open(args.os_vs_oc, None, db.DB_HASH, db.DB_CREATE)
        for taxid in good_tax_ids:
            bdb_creation(os_vs_oc_bdb, nodes, taxid)
        # Close database
        os_vs_oc_bdb.close()