import Pyro4
import hashlib
from threading import Timer

def sha256_hash(s):
    return int(hashlib.sha256(s.encode()).hexdigest(), 16)

class Tracker(object):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.node_id = sha256_hash(self.ip + ':' + str(self.port))
        self.sucessor = '' # 'IP:PORT'
        self.predecessor = '' # 'IP:PORT'
        # keys are the concatenation of sha1 hash of the pieces of the files, pieces key in .torrent
        # values ip and port of the peers that potentially have the piece  , list of tuples (ip,port)
        self.database = {}

<<<<<<< HEAD
    def run_chord(self):
        self.stabilize()
        self.fix_finger()
        self.check_predecessor()
        print('esta es la finger_table')
        print(self.finger_table)
        Timer(1, self.run_chord, []).start()
        
    
    def join(self, ip, port) -> None:
        tracker_proxy = self.connect_to(ip, port, 'tracker')
        print(str(self.node_id) + 'algo!!!!!!!!!!!!!!')
        self.successor = tracker_proxy.find_successor(self.node_id)[1]


    def distribute_information():
        
        


    # def find_predecessor(self, key):
    #     node_id = self.node_id
    #     sucessor = sha256_hash(self.successor)
    #     while key not in range(node_id+1, sucessor+1):
    #         node_id = self.closest_preceding_finger(key)
    #         tracker_proxy = self.connect_to(node_id.split(":")[0], node_id.split(":")[1], 'tracker')
    #         sucessor = self.sha256_hash(tracker_proxy.get_succesor())
    #     return node_id

    def closest_preceding_finger(self, id):
        for i in range(len(self.finger_table)-1, -1, -1):
            if self.finger_table[i][0] in range(self.node_id+1, id):
                return self.finger_table[i]
        return [self.node_id,self.ip+':'+str(self.port)]

    @Pyro4.expose
    def find_successor(self, key):
        print("find succesor")
        print(self.successor)
        successor = self.successor
        node_id = self.node_id
        if node_id == sha256_hash(successor):
            return [node_id, self.ip+":"+str(self.port)]
        print(node_id)
        print(key)
        print(sha256_hash(successor))
        if key in range(node_id+1, sha256_hash(successor)+1):
            print("sucessor:" + successor)
            return (sha256_hash(successor), successor)
        elif sha256_hash(self.predecessor) > self.node_id:
            return [node_id, self.ip+":"+str(self.port)] 
        else:
            node_id = self.closest_preceding_finger(key)[1]
            tracker_proxy = self.connect_to(node_id.split(":")[0], int(node_id.split(":")[1]), 'tracker')
            return tracker_proxy.find_successor(key)
    
    def stabilize(self):
        print("stabilize")
        print(self.successor)
        print(self.predecessor)
        tracker_proxy = self.connect_to(self.successor.split(":")[0], int(self.successor.split(":")[1]), 'tracker')
        successor_predecessor = tracker_proxy.get_predecessor()

        if sha256_hash(successor_predecessor) in range(self.node_id+1, sha256_hash(self.successor)) or (self.predecessor != "" and sha256_hash(self.successor)==self.node_id):
            self.successor = successor_predecessor
        
        tracker_proxy = self.connect_to(self.successor.split(":")[0], int(self.successor.split(":")[1]), 'tracker')
        print('voy a entrar a notificar')
        tracker_proxy.notify(self.ip+":"+str(self.port))

    @Pyro4.expose
    def notify(self, node):
        print("notify")
        print('Estoy printeando node: %s', node)

        if not self.predecessor or sha256_hash(self.predecessor) == self.node_id or sha256_hash(node) in range (sha256_hash(self.predecessor), self.node_id):
            self.predecessor = node
        print(self.successor)
        print(self.predecessor)


    def fix_finger(self):
        print("fix_finger")
        self.next_to_fix += 1
        if self.next_to_fix > 3:
            self.next_to_fix = 1

        self.finger_table[self.next_to_fix] = self.find_successor(self.node_id+2**(self.next_to_fix-1))
        

    def check_predecessor(self):
        print("check predecessor")
        try:
            tracker_proxy = self.connect_to(self.predecessor.split(":")[0], int(self.predecessor.split(":")[1]), 'tracker')
            print("predeccesor checked")
        except:
            self.predecessor = ""
    
    @Pyro4.expose
    def get_successor(self):
        return self.successor

    @Pyro4.expose
    def get_predecessor(self):
        return self.predecessor
   
    

   


=======
>>>>>>> 5a27bd1cda24ac7742f7a60e5c362ce92b7ad5d9
    @Pyro4.expose
    def get_peers(self, pieces_sha1):
        peers = self.database[pieces_sha1]

        return peers

    @Pyro4.expose
    def add_to_database(self, pieces_sha1, ip, port):
        print(type(pieces_sha1))
        if pieces_sha1 in self.database.keys():
            print("llegue aqui")
            if not (ip,port) in self.database[pieces_sha1]:
                self.database[pieces_sha1].append((ip, port))

        else:
            self.database[pieces_sha1] = [(ip, port)]


    def remove_from_database(self, pieces_sha1, ip, port):
        if pieces_sha1 in self.database.keys():
            if not (ip,port) in self.database[pieces_sha1]:
                self.database[pieces_sha1].remove((ip, port))

    def add_to_trackers(self, pieces_sha1, ip, port):
        pieces_sha256 = sha256_hash(pieces_sha1)
        if self.sucessor == '':
            self.add_to_database(pieces_sha256, ip, port)

    def join(self, ip, port):
        proxy_tracker = self.connect_to(ip, port, 'tracker')
        start_tracker_id = proxy_tracker.node_id
        if (start_tracker_id > self.node_id):
           while(proxy_tracker.node_id > self.node_id):
               actual_node_id = proxy_tracker.node_id
               
               ip_next, port_next = proxy_tracker.predecessor.split(':')
               proxy_tracker = self.connect_to(ip_next, int(port_next), 'tracker')
               if proxy_tracker.node_id>actual_node_id:
                   self.chord_neighbors_update(ip_next, port_next)
        else:
            while(proxy_tracker.node_id < self.node_id):
                actual_node_id = proxy_tracker.node_id
                
                ip_next, port_next = proxy_tracker.sucessor.split(':')
                proxy_tracker = self.connect_to(ip_next, int(port_next), 'tracker')
                if proxy_tracker.node_id<actual_node_id:
                    self.chord_neighbors_update(ip_next, port_next, is_predecessor= False)
               
               
    def chord_neighbors_update(self, ip, port, is_predecessor : bool = True):
        if 
    
    
    @Pyro4.expose
    def dummy_response(self):
        return "DUMMY RESPONSE"

    
    def connect_to(self, ip, port, type_of_peer):
        ns = Pyro4.locateNS()
        # by default all peers, including tracker are registered in the name server as type_of_peerIP:Port
        uri = ns.lookup(f"{type_of_peer}{ip}:{port}")
        proxy = Pyro4.Proxy(uri=uri)

        # try:
        #     tracker_proxy._pyroConnection.ping()
        #     print(f"Succefuly connection with the TRACKER at {tracker_ip}:{tracker_port}")
        # except Pyro4.errors.CommunicationError:
        #     print("TRACKER Unreachable")

        return proxy


# tracker = Tracker("127.0.0.1", 6200)

# daemon = Pyro4.Daemon(host=tracker.ip, port= tracker.port)
# ns = Pyro4.locateNS()
# uri = daemon.register(tracker)
# ns.register(f"tracker{tracker.ip}:{tracker.port}", uri)
# print(f"TRACKER {tracker.ip}:{tracker.port} STARTED")
# daemon.requestLoop()
