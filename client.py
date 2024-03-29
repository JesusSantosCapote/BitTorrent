import Pyro4
import os
import math
import random
import serpent
import base64
from bclient_logger import logger
from torrent_files_utils.torrent_creator import TorrentCreator
from torrent_files_utils.torrent_reader import TorrentReader
from torrent_files_utils.torrent_info import TorrentInfo
from piece_manager import PieceManager
from data_structs.block import Block, BlockState, DEFAULT_BLOCK_SIZE


actual_path = os.getcwd()

class BitTorrentClient:
    

    
    
    def __init__(self, ip, port):
        self.ip = ip 
        self.port = port
        self.peers = []

        #TODO:Put more trackers on .torrent 


    def update_trackers(self, trackers, sha1, remove : bool = False):
        if remove:
            for tracker_ip, tracker_port in trackers:
                tracker_proxy = self.connect_to(tracker_ip, tracker_port, 'tracker')
                tracker_proxy.remove_from_database(sha1, self.ip, self.port)
        else:
            print('estoy haciendo update trackers')
            for tracker_ip, tracker_port in trackers:
                tracker_proxy = self.connect_to(tracker_ip, tracker_port, 'tracker')
                tracker_proxy.add_to_trackers(sha1, self.ip, self.port)
            
    def upload_file(self, path, tracker_urls, private = False, comments = "unknow", source = "unknow" ):
        '''
        Upload a local file to the tracker
        '''
        tc = TorrentCreator(path, 1 << 18, private, tracker_urls, comments, source )
        sha1_hash = tc.get_hash_pieces()
        tc.create_dottorrent_file('torrent_files')

        trackers = []

        for url in tracker_urls:
            ip, port = url.split(':')
            trackers.append((ip, int(port)))
        print(type(trackers))
        print(trackers)
        print('vamos a llamar a update trackers')
        self.update_trackers(trackers, sha1_hash)


    def get_peers_from_tracker(self, torrent_info):
        info = torrent_info
        peers = []
        trackers = info.get_trackers()
        peers = []
        for tracker_ip, tracker_port in trackers:
            tracker_proxy = self.connect_to(tracker_ip, tracker_port, 'tracker')
            for peer in tracker_proxy.get_peers(info.metainfo['info']['pieces']):
                peers.append(peer)
        return peers
            # ahora tengo que conectarme al peers y preguntarle por las piezas que tiene
            #para elegir la mas rara para descargarla
            
        #TODO:Check this method, and potential connection failures
    def find_rarest_piece(self, peers, torrent_info : TorrentInfo, owned_pieces):
        count_of_pieces = [0 for i in range(torrent_info.number_of_pieces)]
        owners = [[] for i in range(torrent_info.number_of_pieces)]
        print(peers)
        for ip, port in peers:
            proxy = self.connect_to(ip, port, 'client')
            print('voy a hacer get_bit_field')
            peer_bit_field = proxy.get_bit_field_of(dict(torrent_info.metainfo['info']))
            print('tengo el bitfield')
            print(peer_bit_field)
            for i in range(len(peer_bit_field)):
                if peer_bit_field[i]:
                    count_of_pieces[i] = count_of_pieces[i] + 1
                    owners[i].append((ip, port))
            rarest_piece = count_of_pieces.index(min(count_of_pieces))
            while(owned_pieces[rarest_piece]):
                count_of_pieces[rarest_piece] = math.inf
                rarest_piece = count_of_pieces.index(min(count_of_pieces, lambda x:x))
        return rarest_piece, owners[rarest_piece]


    def dowload_file(self, dottorrent_file_path, save_at = 'client_files' ):
        '''
        Start dowload of a file from a local dottorrent file
        '''
        tr = TorrentReader(dottorrent_file_path)
        info = tr.build_torrent_info()
        peers = self.get_peers_from_tracker(info)
        piece_manager_inst = PieceManager(info.metainfo['info'], save_at)
        
        self.update_trackers(info.get_trackers(), info.dottorrent_pieces)
        
        while not piece_manager_inst.completed:
            rarest_piece, owners = self.find_rarest_piece(peers, info, piece_manager_inst.bitfield)
            while len(owners)>0:
                print('tengo un owner')
                peer_for_download = owners[random.randint(0,len(owners)-1)]
                owners.remove(peer_for_download)
                #try:
                piece_manager_inst.clean_memory(rarest_piece)
                print('voy a tratar de descargar la pieza')
                self.dowload_piece_from_peer(peer_for_download, info, rarest_piece, piece_manager_inst)
                break
                # except:
                #     logger.error('Download error')
            if not len(owners):
                break
            
   
    def dowload_piece_from_peer(self, peer, torrent_info : TorrentInfo, piece_index, piece_manager : PieceManager):
        try:
            proxy_peer = self.connect_to(peer[0], peer[1], 'client')
        except:
            logger.error("Connection failure")
            return
        piece_size = torrent_info.file_size % torrent_info.piece_size if piece_index == piece_manager.number_of_pieces - 1 else torrent_info.piece_size
        for i in range(int(math.ceil(float(piece_size) / DEFAULT_BLOCK_SIZE))):
            received_block = proxy_peer.get_block_of_piece(dict(torrent_info.metainfo['info']), piece_index, i*DEFAULT_BLOCK_SIZE)
            print('este es el bloque que me mandaron')
            print(received_block)
            raw_data = base64.b64decode(received_block['data']['data'])
            piece_manager.receive_block_piece(piece_index, i*DEFAULT_BLOCK_SIZE, raw_data)
    
        
            
    #TODO: Check if the path must cointain /
    @Pyro4.expose
    def get_bit_field_of(self, info):
        piece_manager = PieceManager(info, 'client_files')
        return piece_manager.bitfield
            

    # def get_piece_of_file(self, torrent_info : TorrentInfo, piece_index):
    #     piece_manager = PieceManager(torrent_info, '/client_files')
    #     return piece_manager.get_piece(piece_index)
    
    #TODO: Check if the path must cointain /
    @Pyro4.expose
    def get_block_of_piece(self, info, piece_index, block_offset):
        piece_manager = PieceManager(info, 'client_files')
        print('la pieza tiene estos bloques')
        print(piece_manager.pieces[piece_index].number_of_blocks)
        print(piece_manager.get_block_piece(piece_index, block_offset).data)
        return piece_manager.get_block_piece(piece_index, block_offset)

    ###Testing scope

    @Pyro4.expose
    def pyro_tester(self, a):
        return a
    
    def pyro_tester_caller(self, a):
        proxy_peer = self.connect_to('127.0.0.1', 6201, 'client')
        s = proxy_peer.pyro_tester(a)
        return s
    ###Testing scope

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
    