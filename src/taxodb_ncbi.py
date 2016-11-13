#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Corinne Maufrais
# Institut Pasteur, DSI/CIB
# maufrais@pasteur.fr
# Updated by Emmanuel Quevillon <tuco@pasteur.fr>

from __future__ import print_function
import sys
import argparse
from bsddb3 import db                   # the Berkeley db data base
from time import time


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
            if taxid != '1' and taxid in nodes:
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
        print("WARNING: Not in AUTH_OS_NAMES for %s" % taxid)
        return nodes[taxid]['names'].keys()[0][0]


def print_line(outfh, line, tag, car=80):
    i = 0
    while i < len(line):
        st = line[i:i+car-5]
        if st[-1] in (';', ' ', '\n'):
            print('%s   %s' % (tag, st.strip()), file=outfh)
        else:
            while st[-1] not in (';', ' '):
                st = st[:-1]
                i -= 1
            print('%s   %s' % (tag, st.strip()), file=outfh)
        i += car - 5


def flat_db_creation(taxodbfh, nodes, taxid, car=80):
    li, OC = extract_LI_and_OC(nodes, taxid)
    print('ID   %s;' % taxid, file=taxodbfh)
    print('XX', file=taxodbfh)
    print_line(taxodbfh, li, 'LI', car=car)
    print('XX', file=taxodbfh)
    OS = extract_OS(nodes, taxid)
    print('OS   %s;' % OS, file=taxodbfh)
    print_line(taxodbfh, OC, 'OC', car=car)
    print('//', file=taxodbfh)


def table_creation(os_vs_oc_fh, nodes, taxid):
    li, OC = extract_LI_and_OC(nodes, taxid)
    for LOS in nodes[taxid]['names'].values():
        for OS in LOS:
            print('%s\t %s' % (OS, OC), file=os_vs_oc_fh)


def bdb_creation(os_vs_oc_bdb, nodes, taxid):
    li, OC = extract_LI_and_OC(nodes, taxid)
    for LOS in nodes[taxid]['names'].values():
        for OS in LOS:
            os_vs_oc_bdb.put(OS, OC)


def parse_nodes(nodesfh, fmt='full'):
    nodes = {}
    good_tax_ids = []

    line = nodesfh.readline()
    while line:
        fld = line[:-1].split('\t|\t')
        if fld[0] in nodes:
            print("WARNING: Duplicate tax_id: %s" % fld[0], file=sys.stderr)
        else:
            nodes[fld[0]] = {'id_parent': fld[1], 'rank': fld[2], 'names': {}}
            if fmt == 'full':
                if (fld[2] == 'species' or fld[2] == 'no rank' or fld[2] == 'subspecies') and fld[0] != '1':
                    good_tax_ids.append(fld[0])
            else:
                if fld[0] != '1':
                    good_tax_ids.append(fld[0])
            # if fld[0] != '1':
            #     if fmt == 'full':
            #         if fld[2] in ['species', 'no rank', 'subspecies']:
            #             good_tax_ids.append(fld[0])
            #     else:
            #         good_tax_ids.append(fld[0])


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
            print("WARNING: No corresponding tax_id: %s" % fld[0], file=sys.stderr)
        line = namesfh.readline()
    return nodes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='taxodb_ncbi.py',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="program uses to format the NCBI Taxonomy Database")

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
                                 ) 
    general_options.add_argument("-t", "--tab",
                                 dest="os_vs_oc_fh",
                                 help="Output file: tabulated format. Organism with classification.",
                                 metavar="File",
                                 type=argparse.FileType('w'),
                                 )
    general_options.add_argument("-b", "--bdb",
                                 dest="os_vs_oc",
                                 help="Output file: Berleley db format",
                                 metavar="File",
                                 )
    general_options.add_argument("-f", "--format",
                                 dest="format",
                                 help="""
                                 By default, reports only full taxonomy ie taxonomies that have 'species',
                                 'subspecies' or 'no rank' at the final position.
                                 Otherwise, reports all taxonomies even if they are partial""",
                                 metavar="string",
                                 type=str,
                                 choices=['full', 'partial'],
                                 default='full'
                                 )
    general_options.add_argument("-v", "--verbose",
                                 dest="verbose",
                                 help="Set verbose mode on, default off",
                                 action="store_true",
                                 default=False)

    try:
        args = parser.parse_args()
    except IOError as msg:
        print("Error: %s" % msg, file=sys.stderr)
        sys.exit(1)

    # ####### TO DO
    #    format verification: names.dmp and nodes.dmp
    # ##########

    if args.taxodbfh or args.os_vs_oc_fh or args.os_vs_oc:
        if args.verbose:
            print("Parsing nodes.dmp ...")
        nodes, good_tax_ids = parse_nodes(args.nodesfh, fmt=args.format)
        if args.verbose:
            print("Parsing names.dmp ...")
        nodes = parse_names(args.namesfh, nodes)
    else:
        print("Nothing  specified, quit!", file=sys.stderr)
        sys.exit(1)

    if args.taxodbfh:
        for taxid in good_tax_ids:
            flat_db_creation(args.taxodbfh, nodes, taxid)

    if args.os_vs_oc_fh:
        for taxid in good_tax_ids:
            table_creation(args.os_vs_oc_fh, nodes, taxid)

    if args.os_vs_oc:
        # Get an instance of BerkeleyDB
        os_vs_oc_bdb = db.DB()
        # Create a database in file "osVSocDB" with a Hash access method
        #       There are also, B+tree and Recno access methods
        try:
            os_vs_oc_bdb.open(args.os_vs_oc, None, db.DB_HASH, db.DB_CREATE, mode=0666)
        except db.DBAccessError as msg:
            print("Error: %s %s" % (args.os_vs_oc, msg), file=sys.stderr)
            os_vs_oc_bdb.close()
            sys.exit(1)

        if args.verbose:
            print("Creating Berkeley database ... ")
        for taxid in good_tax_ids:
            bdb_creation(os_vs_oc_bdb, nodes, taxid)
        # Close database
        os_vs_oc_bdb.close()
