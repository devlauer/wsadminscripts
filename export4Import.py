import sys
import util

print "---------------------------------------------------------------"
print " export4Import (Namespacebindings, AuthData, JDBCProviders, Datasources"
print " "
print " Usage: wsadmin -lang jython -f export4Import.py <target server name> <target server node> <localpath to security.xml>"
print "        writes a file named import.py in the same directory for import"
print "---------------------------------------------------------------"
print " "
print " "
if(sys.argv[0]==None):
    print "Missing target server name"
    sys.exit(2)
if(sys.argv[1]==None):
    print "Missing target server node name"
    sys.exit(2)
if(sys.argv[2]==None):
    print "Missing absolute path to security.xml"
    sys.exit(2)

# result names
server = sys.argv[0]
node = sys.argv[1] 

# input path
securityXML = sys.argv[2] 

# result file
outputFile = open('import.py','w')
outputFile.write('import util\n')

r = util.listNamespaces()
for line in r:
    name = line[0]
    namespace = line[1]
    value = line[2]
    outputString = 'util.addBindingsToServer("%s","%s","%s","%s")\n' % (server, name, namespace, value)
    outputFile.write(outputString)
outputFile.write('util.saveConfig()\n')


auth = util.listAuthData()
for a in auth:
    alias = a[0]
    password = util.searchPassword(alias,securityXML)
    user = a[1]
    outputString = 'util.addJAASAuthData("%s","%s","%s")\n' % (alias, user, password)
    outputFile.write(outputString);
outputFile.write('util.saveConfig()\n')

r = util.listJdbcProviders()
for line in r:
    providerClasspath = line[0]
    providerImplementationClassName = line[2]
    providerName = line[4]
    providerNativeClasspath = line[5]
    providerType = line[6]
    providerXA = line[7]
    if providerType == None:
        providerType = ''
    outputString = 'util.addJDBCProvider("%s","%s","%s","%s","%s","%s","%s","%s")\n' % (node, server, providerClasspath, providerImplementationClassName,providerName, providerNativeClasspath, providerType, providerXA)
    outputFile.write( outputString)
outputFile.write('util.saveConfig()\n')
ds = util.listDatasources()
for d in ds:
    name= d[0]
    jndi = d[1]
    authalias = d[2]
    if authalias == None:
        authalias=''
    provider = d[3]
    db = d[4]
    driverType = d[5]
    dbserver = d[6]
    dbport = d[7]
    dsDatasourceHelperClassname=d[8]
    dsProviderType=d[9]
    outputString = 'util.addDataSource("%s","%s","%s","%s","%s","%s","%s",%i,"%s",%i,"%s","%s")\n' % (node,server,name, jndi, authalias, provider, db, driverType, dbserver, dbport,dsDatasourceHelperClassname,dsProviderType)
    outputFile.write(outputString)
outputFile.write('util.saveConfig()\n')
    
outputFile.close()

