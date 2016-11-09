import sys
import string

def changeDBInNamespaces(serverold,servernew,portold,portnew):         
    "changes all server and port occurances in namespacebindings"
    namespaces=AdminConfig.list( 'NameSpaceBinding' ).splitlines()
    namespaceslist=[]
    for ns in namespaces :
        name = AdminConfig.showAttribute( ns, 'name' )
        nameInNameSpace = AdminConfig.showAttribute( ns, 'nameInNameSpace')
        stringToBind = AdminConfig.showAttribute( ns, 'stringToBind' )
        if stringToBind==None:
            print "Ignoring %s as it has no string to bind" % (name)
            continue
        if stringToBind.find(serverold) >= 0:
            stringToBind = string.replace(stringToBind,serverold,servernew)
            stringToBind = string.replace(stringToBind,portold,portnew)
            print "Changing binding %s" % name
            AdminConfig.modify(ns, [['name', name], ['nameInNameSpace', nameInNameSpace], ['stringToBind', stringToBind]])

def cangeDatasources(serverold,servernew,portold, portnew):
    "changes all server and port occurances in datasources"
    datasources = []
    dsentries = AdminConfig.list("DataSource").splitlines()
    for dsentry in dsentries:
        dsname = AdminConfig.showAttribute(dsentry, "name")
        dsAuthMechanismPreference = AdminConfig.showAttribute(dsentry, "authMechanismPreference")
        dsCategory = AdminConfig.showAttribute(dsentry, "category")
        dsJNDIName = AdminConfig.showAttribute(dsentry,"jndiName")
        dsProperties = AdminConfig.showAttribute(dsentry,"properties")
        dsPropertySet = AdminConfig.showAttribute(dsentry,"propertySet")
        propList = AdminConfig.list('J2EEResourceProperty', dsPropertySet).splitlines()
        dbName=''
        serverName=''
        portNumber=0
        for prop in propList:
            name = AdminConfig.showAttribute(prop, 'name')
            if name == 'databaseName':
                dbName = AdminConfig.showAttribute(prop, 'value')   
            elif name == 'serverName':
                serverName = AdminConfig.showAttribute(prop, 'value')
            elif name == 'portNumber':
                portNumber = AdminConfig.showAttribute(prop, 'value')
        # only add Database Datasources to the list
        if dbName == None:
            print "DataSource %s has no databaseName, it is skipped!" % (dsname)
            continue
        if serverName == serverold:
            print "Changing DataSource %s from %s to Server %s" % (dsname,serverold,servernew)
            for prop in propList:
                name = AdminConfig.showAttribute(prop, 'name')
                if name == 'serverName':
                    AdminConfig.modify(prop, [['value',servernew]])
                elif name == 'portNumber':
                    AdminConfig.modify(prop, [['value', portnew]])

def changeJdbcProviders(olddriver,newdriver):
    "changes all driver jars for all jdbc providers if they have the specified driver-jar-name"
    providerList=[]
    providerEntries = AdminConfig.list( "JDBCProvider" ).splitlines()
    for provider in providerEntries:
        providerClasspath = AdminConfig.showAttribute( provider, "classpath" )
        if providerClasspath.find(olddriver)>=0:
            providerClasspathNew = string.replace(providerClasspath,olddriver,newdriver)
            print "Changing JDBCProvider Classpath old: %s Classpath new %s" % (providerClasspath,providerClasspathNew)
            AdminConfig.modify(provider,[['classpath',[]]])
            AdminConfig.modify(provider,[['classpath',providerClasspathNew]])

print "---------------------------------------------------------------"
print " changeDatabase replace drivername, servername and port"
print " "
print " Usage: wsadmin -lang jython -f changeDB.py <old servername> <target servername> <old port> <target port> <old drivername> <target drivername>"
print "        "
print "---------------------------------------------------------------"
print " "
print " "
if(sys.argv[0]==None):
    print "Missing old server name"
    sys.exit(2)
if(sys.argv[1]==None):
    print "Missing target server name"
    sys.exit(2)
if(sys.argv[2]==None):
    print "Missing old port"
    sys.exit(2)
if(sys.argv[3]==None):
    print "Missing target port"
    sys.exit(2)
if(sys.argv[4]==None):
    print "Missing old drivername"
    sys.exit(2)
if(sys.argv[5]==None):
    print "Missing target drivername"
    sys.exit(2)
    
old_servername = sys.argv[0]
target_servername = sys.argv[1] 
old_port = sys.argv[2]
target_port = sys.argv[3] 
old_drivername = sys.argv[4]
target_drivername = sys.argv[5] 
changeDBInNamespaces(old_servername,target_servername,old_port,target_port)
cangeDatasources(old_servername,target_servername,old_port,target_port)
changeJdbcProviders(old_drivername,target_drivername)
if (AdminConfig.hasChanges()):
    AdminConfig.save()
print "changed everything"


