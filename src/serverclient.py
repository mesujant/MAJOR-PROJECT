from multiprocessing import Process
import Pyro4
from cassandra.cluster import Cluster
import datetime
from threading import Thread
from random import randint
from termcolor import colored
import hashlib


class Server(Process):
    def __init__(self,nodeIp):
        self.nodeIp = nodeIp
        Process.__init__(self)
        pass
    def run(self, *args, **kwargs):
        Pyro4.Daemon.serveSimple({ServerMethod(self.nodeIp) : 'Server'},host= self.nodeIp,  port= 12000, ns=False, verbose= True)
        return Process.run(self, *args, **kwargs)

class Client(Process):
    def __init__(self,nodeIp):
        self.nodeIp = nodeIp
        Process.__init__(self)
        pass
    def run(self, *args, **kwargs):
        ClientMethod.nodeIp.append(self.nodeIp)
        ClientMethod.myIp = self.nodeIp
        Pyro4.Daemon.serveSimple({ClientMethod : 'Client'},host=self.nodeIp, port= 14000, ns=False, verbose= True)
        return Process.run(self, *args, **kwargs)

class ServerClient(Process):
    def __init__(self,choise,nodeIp):
        self.choise = choise
        self.nodeIP = nodeIp
        Process.__init__(self)
        pass
        
    def run(self, *args, **kwargs):
        print("From ServerClient  choise={0}  port={1}".format(self.choise,self.nodeIP))
        cluster = Cluster()
        session = cluster.connect('database')
        session.execute('drop table IF  EXISTS blockchain_'+self.nodeIP.replace('.','_'))
        session.execute("CREATE TABLE  blockchain_"+ self.nodeIP.replace('.','_') +" (mykey text  ,data text,prev_key text,insert_time timestamp, primary key(insert_time)) ;") #WITH CLUSTERING ORDER BY (count  DESC)
        session.shutdown()
        #cluster = Cluster()
        #stament = cluster.connect('database')
        #stament.execute("CREATE TABLE IF NOT EXISTS blockchain_{0} (mykey text primary key ,data text,prev_key text);".format(self.port))
        if self.choise == 1:
            #change = NetworkChange(port=self.port)
            #change.start()
            #print("Network Change Should be started")
            Server(nodeIp=self.nodeIP).start()
            print("Server and Client started")
        Client(nodeIp=self.nodeIP).start()
        print('client started')
        return Process.run(self, *args, **kwargs)
    
class Consensus(Thread):
        
    def initValue(self,nodeIp,queVal,caller,requestTime):
        self.nodeIp = nodeIp
        self.requestTime = requestTime
        self.queVal = queVal
        self.caller = caller
        
    def run(self):
        Thread.run(self)
        #print((self.nodeIp,self.queVal,self.caller,self.requestTime))
        print(colored("Sending consensus request to Ip {0} at time {1} ".format(self.nodeIp,datetime.datetime.now())),'red')
        client = Pyro4.core.Proxy('PYRO:Client@' + self.nodeIp + ':14000')
        
        result = client.factorial(self.queVal)
        #print(colored("Result of port {0} is {1} at time {2}".format(self.args[0],result,datetime.datetime.now())),'red')
        self.caller.consensusWinner(self.nodeIp,self.requestTime)
        
    
@Pyro4.expose  
class ServerMethod:
    prevKey = '000000'
    def __init__(self,nodeIp):
        self.nodeIp = [nodeIp,]
        self.myIp = nodeIp
        self.requtest = {}
        pass
    def setPreviousKey(self,key):
        ServerMethod.prevKey = key 
        pass
    
    def getPreviousKey(self):
        return ServerMethod.prevKey
        pass
    
    def addNode(self,nodeIp):
        for node in self.nodeIp:
            client = Pyro4.core.Proxy('PYRO:Client@' + node + ':14000')
            client.addNode(nodeIp)
        self.nodeIp.append(nodeIp)
        print("From ServerMethod Add NODE   {0}".format(nodeIp))
        self.copyPort(nodeIp)
        pass
    
    def removeNode(self,port):
        print("From ServerMethod Remove NODE   {0}".format(port))
        pass
    
    def changeServer(self):
        print("From ServerMethod Change NODE   ")
        
        pass
    
    def copyBlock(self,port):
        pass
    
    def copyPort(self,nodeIp):
        client = Pyro4.core.Proxy('PYRO:Client@' + nodeIp + ':14000')
        for ip in self.nodeIp:
            client.copyPort(ip)
        pass
    
    def addBlock(self,data):
        print("Add Bloc is called with data = {0}".format(data))
        requestTime = datetime.datetime.now()
        self.requtest[requestTime] = data
        queVal = randint(50,100)
        '''consensus = Consensus()
        consensus.initValue(list=[self.nodesPort[0]-1,queVal,self,requestTime,])
        consensus.start()

        for p in self.nodesPort[1:]:
            consensus = Consensus()
            consensus.initValue(list=[p,queVal,self,requestTime,])
            consensus.start()
        pass'''
        for node in self.nodeIp:
            consensus = Consensus()
            consensus.initValue(nodeIp=node,queVal=queVal,caller=self,requestTime=requestTime,)
            consensus.start()
            pass
    
    def consensusWinner(self,nodeIp,requestTime):
        
        if requestTime in self.requtest:
            data = self.requtest[requestTime]
            del self.requtest[requestTime]
            print("request time  is  {0} and node ip is {1}".format(requestTime,nodeIp))
            print("Winner is {0} and data is {1}  ".format(nodeIp,data))
            client = Pyro4.core.Proxy('PYRO:Client@' + nodeIp + ':14000')
            client.addBlock(data,requestTime)
            print("Client Block is added by winner {0}".format(nodeIp))
            
        else:
            print("Losser is {0}".format(nodeIp))
        pass
    
    def sentBlockData(self,data):
        pass
    
    def reciveBlockData(self,data):
        pass
    
    def noticeStopHashing(self):
        pass
    
    def validate(self,data):
        pass
    
    def storeInBlockChain(self,data):
        pass
    
    def reciveValidateMassage(self,data):
        pass
    
    pass

@Pyro4.expose
class ClientMethod:
    myIp = ""
    nodeIp = []
    def __init__(self):
        pass
    
    def addNode(self,nodeIp):
        ClientMethod.nodeIp.append(nodeIp)
        print("Client Node add.. Port is {0} current list is {1}".format(nodeIp,self.nodeIp))
        pass
    
    def removeNode(self,port):
        pass
    
    def changeServer(self):
        pass
    
    def copyBlock(self,port):
        pass
    
    def copyPort(self,nodeIp):
        print("message of server ")
        print(nodeIp)
        ClientMethod.nodeIp.append(nodeIp)
        pass
    
    def factorial(self,num):
        print(datetime.datetime.now())
        #print("Time is {0}".format(datetime.Now()))
        
        mul = 1;
        for i in range(1,num):
          mul = mul *i 
        return mul 
    
    def addBlock(self,data,requestTime):
        print('Client Add Blocked is called and node are {0} and argument is '.format(ClientMethod.nodeIp,(data,requestTime)))
        dataHass = self.findHashing(data)
        print('Client addBlock hass is {0}'.format(dataHass))
        #client = Pyro4.core.Proxy('PYRO:Client@' + ClientMethod.nodeIp + str(ClientMethod.nodesPort[0]-1))
        #client.storeInBlockChain([args[0],dataHass])
        print("sever is {0} and it's prevKey is {1}".format(self.nodeIp[0],ServerMethod.prevKey))
        server = Pyro4.core.Proxy('PYRO:Server@' + self.nodeIp[0] + ':12000')
        prevKey = server.getPreviousKey()
        server.setPreviousKey(dataHass)
        for nodeIP in ClientMethod.nodeIp:
            client = Pyro4.core.Proxy('PYRO:Client@' + nodeIP + ':14000')
            client.storeInBlockChain(data,dataHass,prevKey)
        print("Client Ajay Block Added")
        pass
    
    def sentBlockData(self,data):
        pass
    
    def reciveBlockData(self,data):
        pass
    
    def findHashing(self,data):
        
        once = 0
        dataRan = data
        dataHass = hashlib.sha1((dataRan+str(once)).encode()).hexdigest()
        while dataHass[0:2] != '00':
            once = once +1
            dataHass = hashlib.sha1((dataRan+str(once)).encode()).hexdigest()
            pass 
        
        
        return dataHass
    
    def validate(self,data):
        pass
    
    def storeInBlockChain(self,data,hass,prevKey):
        print("Store in blockchain. Data is {0} and key is {1} ".format(data,hass))
        cluster = Cluster()
        session = cluster.connect('database')
        '''prevInfo = session.execute('select mykey,count from blockchain_'+self.myIp.replace('.','_')+";").one()
    
        if prevInfo == None:
            prevKey = ("00000000")
            count = 1
        else:
            prevKey = prevInfo[0]
            count = prevInfo[1]+1
            pass'''
        
        session.execute("insert into blockchain_"+self.myIp.replace('.','_')  +"(mykey,data, prev_key, insert_time) values ('{0}','{1}','{2}','{3}');".format(hass,data,prevKey,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        session.shutdown()
        print("block is store")
        pass
    
    def reciveValidateMassage(self,data):
        pass
    
    pass

if __name__ == "__main__":
    print("ajay sharma")
    choice = int(input("Enter 1 to make server and 2 to make client  "))
    ipList = ['192.168.1.87','192.168.1.2','192.168.1.3','192.168.1.4']
    seq = int(input("Enter ip address seq  "))
    
    server = ServerClient(choise=choice,nodeIp=ipList[seq])
    server.start()
    
    
    