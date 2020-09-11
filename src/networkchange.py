from builtins import input
from multiprocessing import Process
import Pyro4
from os import system






class NetworkChange(Process):   
    def __init__(self,nodeIp):
        self.nodeIp = nodeIp
        self.listener()
        Process.__init__(self)
        
        
    def listener(self): 
        system("clear")    
        print("NetworkChange Started")
        print()
        ipList = ['192.168.1.87','192.168.1.2','192.168.1.3','192.168.1.4']
        print("Enter 1 to Add Node \nEnter 2 to Remove Node \nEnter 3 to AddBlock\nEnter 4 to ServerChange")
        server = Pyro4.core.Proxy('PYRO:Server@' + self.nodeIp + ':12000')
        while True:
            choise =int( input("\nEnter Choise "))
            if choise == 1:
                print("Add Node should be called")
                port = int(input("Enter node ip seq:  "))
                server.addNode(ipList[port])
                pass
            elif choise == 2:
                print("Remove Node should be called")
                port = int(input("Enter port:  "))
                server.removeNode(port = port)
                pass
            elif choise == 3:
                print("Add Block should be called")
                data = input("Enter the data  ")
                server.addBlock(data = data)
                pass
            elif choise == 4:
                print("Server change should be called")
                server.changeServer()
                pass
            elif choise == 5:
                for nodeIp in ipList[1:]:
                    server.addNode(nodeIp)
            
            

if __name__ == '__main__':
    NetworkChange('192.168.1.87')


    
