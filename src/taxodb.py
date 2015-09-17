#! /usr/local/bin/python

# Corinne Maufrais
# Institut Pasteur, Groupe Logisiels et Banques de sonnees
# maufrais@pasteur.fr
#
# version 1

import os, sys, getopt
from bsddb import db                   # the Berkeley db data base

def usage():
    print """
usage: taxodb <files>

options:
   -h          ... Print this message and exit.
   
   -k          ... taxoDB databank creation
   -t          ... special files creation  ( organism versus taxonomy table )
   -b          ... Berleley db creation ( organism versus taxonomy table )
   
   -n <file>   ... Taxonomy names file
   -d <file>   ... Taxonomy nodes file
   

description:
    - Taxonomy NCBI database
    """

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
                
def DBcreation( taxodbfh, nodes, taxid, car = 80 ):
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
    
    
def BDBcreation( osVSocBDB, nodes, taxid ):
    li, OC = extractLIandOC( nodes, taxid )
    #print 'OS' and 'OC'
    for LOS in nodes[ taxid ]['names'].values():
        for OS in LOS:
            osVSocBDB.put(OS,OC)
    
    
    
if __name__=='__main__':
    try:
        opts, args = getopt.gnu_getopt( sys.argv[1:], "hn:d:ktb",["help", "names", "nodes"] )
    except getopt.GetoptError:
        usage()
        sys.exit( 0 )
    
    TAXODB = './'
    #RELEASE = './'
    FLAT = './'
    TABLE = './'
    #namefile = RELEASE+'names.dmp'
    #nodefile = RELEASE+'nodes.dmp'
    namefile = None
    nodefile = None
    taxodbfile = FLAT+'taxodb'
    osVSocfile = TABLE +'taxodb_osVSoc.txt'    #Correspondence between organism and taxonomy. Rapid access.
    #osVSocBDBfile = TABLE +'taxodb_osVSocBDB'
    osVSocBDBfile = TABLE +'taxodb.bdb'
    dbcreation = False
    tablecreation = False 
    berkeleydb = False

    for o, v in opts: #( opt, value )
        if o in ( "-h","--help" ):
            usage()
            sys.exit( 0 )
        elif o in ( "-n","--names" ):
            namefile = v
        elif o in ( "-d","--nodes" ):
            nodefile = v
        elif o in ( "-k","--bank" ):
            dbcreation = True
        elif o in ( "-t","--table" ):
            tablecreation = True
        elif o in ( "-b","--bdb" ):
            berkeleydb = True
        else:
            usage()
            sys.exit( 0 )
    
    if not dbcreation and not tablecreation and not berkeleydb:
        usage()
        sys.exit( 0 )
        
    if not namefile or not nodefile:
        usage()
        sys.exit( 0 )
    
    if not os.access(TAXODB, 0 ):
        os.mkdir( TAXODB )
    if dbcreation and not os.access(FLAT, 0 ):
        os.mkdir( FLAT )
    if (tablecreation or berkeleydb) and not os.access(TABLE, 0 ):
        os.mkdir( TABLE )
    #if not os.access( namefile, 0 ) or not os.access( nodefile, 0 ): #F_OK == 0, X_OK=1, W_OK=2, R_OK=4
    #    sys.exit( 0 )
    
     
    ######## TO DO
    #
    #    names.dmp and nodes.dmp format verification
    #
    ###########
    
    #print 'nodes.dmp parsing'
    nodes = {}
    taxidOFinterest = []
    
    nodefh = open( nodefile )
    
    line = nodefh.readline()
    while line:
        fld = line[:-1].split('\t|\t')
        if nodes.has_key( fld[0]):
            print >>sys.stderr, "WARNING: Duplicate tax_id: %s" % fld[0]
        else:
            # name == {'name class': 'OS'} ex: {'scientific name': 'Theileria parva.'}
            nodes[ fld[0] ]={'id_parent':fld[1], 'rank': fld[2], 'names':{} }
            if (fld[2] ==  'species' or fld[2] ==  'no rank') and fld[0] != '1':
                taxidOFinterest.append( fld[0] )
        line = nodefh.readline()
    nodefh.close()
    
    #print 'names.dmp parsing'
    namefh = open( namefile )
    line = namefh.readline()
    while line:
        fld = line[:-3].split('\t|\t')
        if nodes.has_key( fld[0]):
            if nodes[ fld[0] ]['names'].has_key( fld[3]):    
                nodes[ fld[0] ]['names'][fld[3]].append(fld[1] )# use scientific name if exist
            else:
                nodes[ fld[0] ]['names'][fld[3]]=[fld[1]]
        else:
            print >>sys.stderr, "WARNING: No corresponding tax_id: %s" % fld[0]
        line = namefh.readline()
    namefh.close()
    
    ### Remarks: dbcreation and tablecreation must be dissociated for dbmaint administration 
    
    #print 'databank creation'
    if dbcreation:
        taxodbfh = open( taxodbfile, 'w' )
        for taxid in taxidOFinterest:
            DBcreation( taxodbfh, nodes, taxid )
        taxodbfh.close()
    
    
    #print 'special table creation' as text
    if tablecreation:
        osVSocfh = open (osVSocfile, 'w' )
        for taxid in taxidOFinterest:
            TableCreation( osVSocfh, nodes, taxid )
        osVSocfh.close()
    
    if berkeleydb:
        # Get an instance of BerkeleyDB 
        osVSocBDB = db.DB()
        # Create a database in file "osVSocDB" with a Hash access method
        #       There are also, B+tree and Recno access methods
        osVSocBDB.open(osVSocBDBfile, None, db.DB_HASH, db.DB_CREATE)
        for taxid in taxidOFinterest:
            BDBcreation( osVSocBDB, nodes, taxid )
        # Close database
        osVSocBDB.close()