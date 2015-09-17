#! /usr/local/bin/python

# Corinne Maufrais
# Institut Pasteur, DSI/CIB
# maufrais@pasteur.fr
#
# version 2

import os, sys
import argparse
from bsddb import db                   # the Berkeley db data base




def extractLIandOC( nodes, taxid ):
    li = '' #list of parent taxid
    oc = ''
    while nodes.has_key( taxid ) and taxid !='1':
        if nodes[taxid]['id_parent'] != '1':
            li = nodes[taxid]['id_parent'] + '; ' + li
        if nodes[taxid]['id_parent'] == taxid:
            taxid = '1'
        else:
            taxid = nodes[taxid]['id_parent']
            if taxid != '1':
                if nodes[taxid]['rank'] != 'no rank':
                    oc = "%s (%s); %s" %( extractOSname(nodes, taxid), nodes[taxid]['rank'], oc)
                else:
                    oc = "%s; %s" %( extractOSname(nodes, taxid), oc)
    return li, oc

def extractOSname( nodes, taxid ):
    if nodes[ taxid ]['names'].has_key('scientific name'):
        return nodes[ taxid ]['names']['scientific name'][0] # 80 car
    elif nodes[ taxid ]['names'].has_key('equivalent name'):
        return nodes[ taxid ]['names']['equivalent name'][0]
    elif nodes[ taxid ]['names'].has_key('synonym'):
        return nodes[ taxid ]['names']['synonym'][0]
    elif nodes[ taxid ]['names'].has_key('authority'):
        return nodes[ taxid ]['names']['authority'][0]
    elif nodes[ taxid ]['names'].has_key('common name'):
        return nodes[ taxid ]['names']['common name'][0]
    else:
        return nodes[ taxid ]['names'].keys()[0][0]
        
def printLine( outfh, line, tag, car=80 ):
    i = 0
    while i < len(line):
        st = line[i:i+car-5]
        if st[-1] in (';',' ','\n'):
            print >>outfh, '%s   %s' % (tag, st.strip())
        else:
            while st[-1] not in (';',' '):
                st = st[:-1]
                i -=1
            print >>outfh, '%s   %s' % (tag, st.strip())
        i += car -5
                
def db_creation( taxodbfh, nodes, taxid, car = 80 ):
    li, oc = extractLIandOC( nodes, taxid )
    #print 'ID'
    print >>taxodbfh, 'ID   %s;' % taxid
    print >>taxodbfh, 'XX'
    #print 'LI'
    printLine( taxodbfh, li, 'LI', car )
    print >>taxodbfh, 'XX'
    #print 'OS'
    OS = extractOSname( nodes, taxid )
    print >>taxodbfh, 'OS   %s;' % OS
    #print 'OC'
    printLine( taxodbfh, oc, 'OC', car )
    print >>taxodbfh, '//'
    
    
def TableCreation( osVSocfh, nodes, taxid ):
    li, OC = extractLIandOC( nodes, taxid )
    #print 'OS' and 'OC'
    for LOS in nodes[ taxid ]['names'].values():
        for OS in LOS:
            print >>osVSocfh, '%s\t %s' % (OS, OC)
    
    
def bdb_creation( osVSocBDB, nodes, taxid ):
    li, OC = extractLIandOC( nodes, taxid )
    #print 'OS' and 'OC'
    for LOS in nodes[ taxid ]['names'].values():
        for OS in LOS:
            osVSocBDB.put(OS,OC)
    
    
if __name__=='__main__':
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
    general_options.add_argument("-k", "--bank",
                                 dest="databank",
                                 help="taxoDB databank output.",
                                 action='store_true',
                                 default=False,)
    general_options.add_argument("-t", "--text",
                                 dest="tabulated",
                                 help="text output.",
                                 action='store_true',
                                 default=False,)
    general_options.add_argument("-b", "--bdb",
                                 dest="bdb",
                                 help="Berleley db output",
                                 action='store_true',
                                 default=False,)


    args = parser.parse_args()

    
    TAXODB = './'
    #RELEASE = './'
    FLAT = './'
    TABLE = './'
    taxodbfile = FLAT+'taxodb'
    osVSocfile = TABLE +'taxodb_osVSoc.txt'    #Correspondence between organism and taxonomy. Rapid access.
    #osVSocBDBfile = TABLE +'taxodb_osVSocBDB'
    osVSocBDBfile = TABLE +'taxodb.bdb'
    
    if not args.databank and not args.tabulated and not args.bdb:
        print parser.format_help()
        parser.exit()
    
    if not os.access(TAXODB, 0 ):
        os.mkdir( TAXODB )
    if args.databank and not os.access(FLAT, 0 ):
        os.mkdir( FLAT )
    if (args.tabulated or args.bdb) and not os.access(TABLE, 0 ):
        os.mkdir( TABLE )
    #if not os.access( namefile, 0 ) or not os.access( nodefile, 0 ): #F_OK == 0, X_OK=1, W_OK=2, R_OK=4
    #    sys.exit( 0 )
    
     
    ######## TO DO
    #
    #    names.dmp and nodes.dmp format verification
    #
    ###########
    
    nodes = {}
    good_tax_ids = []
        
    line = args.nodesfh.readline()
    while line:
        fld = line[:-1].split('\t|\t')
        if nodes.has_key( fld[0]):
            print >>sys.stderr, "WARNING: Duplicate tax_id: %s" % fld[0]
        else:
            # name == {'name class': 'OS'} ex: {'scientific name': 'Theileria parva.'}
            nodes[ fld[0] ]={'id_parent':fld[1], 'rank': fld[2], 'names':{} }
            if (fld[2] ==  'species' or fld[2] ==  'no rank') and fld[0] != '1':
                good_tax_ids.append( fld[0] )
        line = args.nodesfh.readline()
    args.nodesfh.close()
    
    #print 'names.dmp parsing'
    line = args.namesfh.readline()
    while line:
        fld = line[:-3].split('\t|\t')
        if nodes.has_key( fld[0]):
            if nodes[ fld[0] ]['names'].has_key( fld[3]):    
                nodes[ fld[0] ]['names'][fld[3]].append(fld[1] )# use scientific name if exist
            else:
                nodes[ fld[0] ]['names'][fld[3]]=[fld[1]]
        else:
            print >>sys.stderr, "WARNING: No corresponding tax_id: %s" % fld[0]
        line = args.namesfh.readline()
    args.namesfh.close()
    
    ### Remarks: args.databank and args.tabulated must be dissociated for dbmaint administration 
    
    # print 'databank creation'
    if args.databank:
        taxodbfh = open( taxodbfile, 'w' )
        for taxid in good_tax_ids:
            db_creation( taxodbfh, nodes, taxid )
        taxodbfh.close()
    
    
    #print 'special table creation' as text
    if args.tabulated:
        osVSocfh = open (osVSocfile, 'w' )
        for taxid in good_tax_ids:
            TableCreation( osVSocfh, nodes, taxid )
        osVSocfh.close()
    
    if args.bdb:
        # Get an instance of BerkeleyDB 
        osVSocBDB = db.DB()
        # Create a database in file "osVSocDB" with a Hash access method
        #       There are also, B+tree and Recno access methods
        osVSocBDB.open(osVSocBDBfile, None, db.DB_HASH, db.DB_CREATE)
        for taxid in good_tax_ids:
            bdb_creation( osVSocBDB, nodes, taxid )
        # Close database
        osVSocBDB.close()