
def getServerName(srv):
    "Evaluates the complete server config id"
    s = AdminConfig.list('Server',srv+'*')
    return s 

def addJAASAuthData(alias, uid, password, replace=0):
    "Adds or replaces some authdata at cell scope"
    cell = AdminConfig.list("Cell")
    cellName = AdminConfig.showAttribute(cell, "name")
    sec = AdminConfig.getid("/Cell:"+cellName+"/Security:/")
    jaasAuthData = AdminConfig.list("JAASAuthData").splitlines()
    for authDataEntry in jaasAuthData:
        authDataEntries = AdminConfig.showAttribute(authDataEntry, "alias").splitlines()
        for authAliasEntry in authDataEntries:
            if ( authAliasEntry == alias):
                if replace:
                    print "Removing existing AuthData %s!" % (alias)
                    AdminConfig.remove(authDataEntry)
                else:
                    print "AuthData %s already exists" % alias
                    return
    attrs = [["alias", alias], ["userId", uid], ["password", password]]
    if (len(sec) > 0):
        print "Adding JAASAuthData with alias %s" % alias
        jaasAuthData  = AdminConfig.create("JAASAuthData", sec, attrs)
        


    
# Add binding
def addBindingsToServer(s,bindingName,bindingNameSpace,bindingValue,replace=0):
    "Adds or replaces a stringnamespacebinding at server scope"
    for ns in AdminConfig.list( 'NameSpaceBinding' ).splitlines() :
        if bindingName == AdminConfig.showAttribute( ns, 'name' ):
            if replace :
                print "Removing existing binding from Server %s" % s
                AdminConfig.remove(ns)
            else :
                print "NameSpaceBinding %s already exists. Skipped adding!" % (bindingName)
                return

    # Create binding
    print "Adding binding to Server %s" % s
    print AdminConfig.create('StringNameSpaceBinding', getServerName(s), [['name', bindingName], ['nameInNameSpace', bindingNameSpace], ['stringToBind', bindingValue]])

def addDataSource(node,s,name,jndiName,authAlias,provider,databaseName,driverType,dbserver,dbport,dsDatasourceHelperClassname,dsProviderType, replace=0):
    "Adds or replaces a datasource at server scope"
    ds = AdminConfig.getid("/Node:"+node+"/Server:"+s+"/JDBCProvider:"+provider+"/DataSource:"+name+"/")
    parentID = AdminConfig.getid("/Node:"+node+"/Server:"+s+"/JDBCProvider:"+provider+"/")
    if(len(parentID) !=0):
        if authAlias == '':
            authAlias=None
        if (len(ds)!=0):
            if replace :
                print "Removing existing DataSource %s!" % (name)
                AdminConfig.remove(ds)
            else :
                print "DataSource %s already exists on server %s" % (name,s)
                return
           
        print "Adding DataSource %s to Server %s" % (name,s)
        propertySet = ['propertySet', [['resourceProperties', [[['name', 'databaseName'], ['type', 'String'], ['value', databaseName]], [['name', 'driverType'], ['type', 'integer'], ['value', driverType]], [['name', 'serverName'], ['type', 'String'], ['value', dbserver]], [['name', 'portNumber'], ['type', 'integer'], ['value', dbport]]]]]]
        dsParameters = [['name', name],['description','scripted by wsadmin'], ['jndiName',jndiName],['authDataAlias',authAlias],['datasourceHelperClassname',dsDatasourceHelperClassname],['providerType',dsProviderType],propertySet]
        dsid =  AdminConfig.create('DataSource',parentID,dsParameters)
    else:
        print "No JDBCProvider found for %s!" % (name)

    
def addJDBCProvider(node,s,classpath,implementationClassName,name,nativepath,type,xa, replace=0):
    "Adds or replaces a jdbc provider at server scope"
    jdbc = AdminConfig.getid("/Node:"+node+"/Server:"+s+"/JDBCProvider:"+name+"/")
    if replace:
        print "Removing JDBCProvider %s from server!" % (name)
        AdminConfig.remove(jdbc)
    else:
        print "JDBCProvider %s already exists on server! Skipped adding!" % (name)
        return
    print "Adding JDBCProvider to Server %s" % s
    print AdminConfig.create('JDBCProvider',getServerName(s),[['name', name],['description','scripted by wsadmin'], ['implementationClassName',implementationClassName],['classpath',classpath],['nativepath',nativepath],['xa',xa],['providerType',type]])
    
def saveConfig():
    "Saves config changes if there are some"
    if (AdminConfig.hasChanges()):
        AdminConfig.save()

def listAuthData():
    "Returns a list of authdata in the form [alias,user]"
    aauthlist = []
    jaasAuthData = AdminConfig.list("JAASAuthData").splitlines()
    for auth in jaasAuthData:
        alias = AdminConfig.showAttribute(auth,'alias')
        user = AdminConfig.showAttribute(auth, 'userId')
        aauthlist.append([alias,user])
    return aauthlist

def searchPassword ( alias, file ):
    "Searches and decrypts a password from a security.xml file of websphere"
    list = []
    password=None
    list.append(alias)
    f=open(file)
    lines=f.readlines()
    for line in lines:
        poz = line.find(alias)
        if poz > 0:
            Line = line
            break
    if Line != None:
        password = Line[Line.find('password=')+15:Line.find('\" description')]
        password = decrypt(password)
    return password

def decrypt ( word ):
    "Decrypts a websphere password"
    if not len(word) > 1: exit()
    word = word.replace(':', '')
    import binascii
    value1 = binascii.a2b_base64(word)
    value2 = '_' * len(value1)
    out = ''
    for a, b in zip(value1, value2):
        out = ''.join([out, chr(ord(a) ^ ord(b))])
    return out        
        
        
def listNamespaces():         
    "Returns a list of all namespacebindings in the form [name, nameInNameSpace, stringToBind]"
    namespaces=AdminConfig.list( 'NameSpaceBinding' ).splitlines()
    namespaceslist=[]
    a=0
    for ns in namespaces :
        name = AdminConfig.showAttribute( ns, 'name' )
        nameInNameSpace = AdminConfig.showAttribute( ns, 'nameInNameSpace')
        stringToBind = AdminConfig.showAttribute( ns, 'stringToBind' )
        if stringToBind==None:
            print "Ignoring %s as it has no string to bind" % (name)
            continue
        namespaceslist.append([name,nameInNameSpace,stringToBind])
        a=a+1
    return namespaceslist

def listJdbcProviders():
    "Returns a list of all jdbc providers in the form [providerClasspath,providerDescription,providerImplementationClassName,providerIsolatedClassLoader,providerName, providerNativeClasspath, providerType, providerXA]"
    providerList=[]
    providerEntries = AdminConfig.list( "JDBCProvider" ).splitlines()
    for provider in providerEntries:
        providerClasspath = AdminConfig.showAttribute( provider, "classpath" )
        providerDescription = AdminConfig.showAttribute( provider, "description" )
        providerImplementationClassName = AdminConfig.showAttribute( provider, "implementationClassName" )
        providerIsolatedClassLoader = AdminConfig.showAttribute( provider, "isolatedClassLoader")
        providerName = AdminConfig.showAttribute( provider, "name" )
        providerNativeClasspath = AdminConfig.showAttribute(provider, "nativepath")
        providerType = AdminConfig.showAttribute(provider, "providerType")
        providerXA = AdminConfig.showAttribute(provider, "xa")
        providerList.append([providerClasspath,providerDescription,providerImplementationClassName,providerIsolatedClassLoader,providerName, providerNativeClasspath, providerType, providerXA])
    return providerList

def listDatasources():
    "Returns a list of all datasources in the form [dsName,dsJNDIName,dsAuthAlias,dsProviderName, dbName, dbDriverType, dbServerName, dbPortNumber,dsDatasourceHelperClassname]"
    datasources = []
    dsentries = AdminConfig.list("DataSource").splitlines()
    for dsentry in dsentries:
        dsAuthAlias = AdminConfig.showAttribute(dsentry, "authDataAlias")
        dsname = AdminConfig.showAttribute(dsentry, "name")
        dsAuthMechanismPreference = AdminConfig.showAttribute(dsentry, "authMechanismPreference")
        dsCategory = AdminConfig.showAttribute(dsentry, "category")
        dsConnectionPool = AdminConfig.showAttribute(dsentry, "connectionPool")
        dsDatasourceHelperClassname = AdminConfig.showAttribute(dsentry, "datasourceHelperClassname")
        dsDescription = AdminConfig.showAttribute(dsentry, "description")
        dsDiagnoseConnectionUsage = AdminConfig.showAttribute(dsentry,"diagnoseConnectionUsage")
        dsJNDIName = AdminConfig.showAttribute(dsentry,"jndiName")
        dsLogMissingTransactionContext = AdminConfig.showAttribute(dsentry,"logMissingTransactionContext")
        dsmanageCachedHandles = AdminConfig.showAttribute(dsentry, "manageCachedHandles")
        dsMapping = AdminConfig.showAttribute(dsentry, "mapping")
        dsPreTestConfig = AdminConfig.showAttribute(dsentry, "preTestConfig")
        dsProperties = AdminConfig.showAttribute(dsentry,"properties")
        dsPropertySet = AdminConfig.showAttribute(dsentry,"propertySet")
        propList = AdminConfig.list('J2EEResourceProperty', dsPropertySet).splitlines()
        dbName=''
        driverType=4
        serverName=''
        portNumber=0
        for prop in propList:
            name = AdminConfig.showAttribute(prop, 'name')
            if name == 'databaseName':
                dbName = AdminConfig.showAttribute(prop, 'value')   
            elif name == 'driverType':
                driverType = AdminConfig.showAttribute(prop, 'value')
            elif name == 'serverName':
                serverName = AdminConfig.showAttribute(prop, 'value')
            elif name == 'portNumber':
                portNumber = AdminConfig.showAttribute(prop, 'value')
        # only add Database Datasources to the list
        if dbName == None:
            print "DataSource %s has no databaseName, it is skipped!" % (dsname)
            continue
        dsProvider = AdminConfig.showAttribute(dsentry,"provider")
        dsProviderName = AdminConfig.showAttribute(dsProvider, "name")
        dsProviderType = AdminConfig.showAttribute(dsentry,"providerType")
        dsRelationalResourceAdapter = AdminConfig.showAttribute(dsentry,"relationalResourceAdapter")
        dsStatementCacheSize = AdminConfig.showAttribute(dsentry,"statementCacheSize")
        dsXARecoveryAuthAlias = AdminConfig.showAttribute(dsentry,"xaRecoveryAuthAlias")
        datasources.append([dsname,dsJNDIName,dsAuthAlias,dsProviderName, dbName, driverType, serverName, portNumber,dsDatasourceHelperClassname,dsProviderType])
    return datasources
