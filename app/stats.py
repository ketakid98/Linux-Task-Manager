import re
import socket
from stat import S_ISSOCK
import subprocess
import time
import pwd
import os

from .common import Common
from .components import IntervalVal, CPU, Disk, Process, NetworkDevice, Connection, Memory 


class CPUStats:
    def __init__(self, file_name="/proc/stat"):
        self.read_time = time.time()
        self.file_name = file_name
        self.cpu_list=[]
        self.interrupts = IntervalVal("interrupts")
        self.context_switches = IntervalVal("context switches")

    def parse_stat_file(self):
        self.stat_file = Common.read_file(self.file_name)
        for l in self.stat_file[1:]:
            if 'cpu' in l[0]:
                try:
                    i = self.cpu_list.index(CPU(l[0]))
                    self.cpu_list[i].update_params(l[1], l[3], l[4], self.read_time)
                except ValueError:
                    temp_cpu = CPU(l[0], l[1], l[3], l[4], self.read_time)
                    self.cpu_list.append(temp_cpu)            
            if 'intr' in l[0]:
                self.interrupts.update_params(l[1], self.read_time)
            if 'ctxt' in l[0]:
                self.context_switches.update_params(l[1], self.read_time)

    def get_sys_wide_cpu_time(self):
        tot = 0
        for cpu in self.cpu_list:
            tot += cpu.sys_wide_time
        return tot/len(self.cpu_list)

    def update_stats(self):
        self.read_time = time.time()
        self.parse_stat_file()

    def get_stats(self):
        self.update_stats()
        print(self.interrupts)
        print(self.context_switches)
        for cpu in self.cpu_list:
            print(cpu)
        print(f"System wide CPU Time: { self.get_sys_wide_cpu_time() }")

    def get_stats_for_gui(self):
        self.update_stats()

        return self.interrupts.get_utilization(), self.context_switches.get_utilization(), self.cpu_list, self.get_sys_wide_cpu_time()

# cpu_stats = CPUStats()
# cpu_stats.get_stats()
# time.sleep(1)
# cpu_stats.get_stats()


class DiskStats:
    def __init__(self, file_name="/proc/diskstats"):
        self.disk_list = []
        self.file_name = file_name
        self.read_time = time.time()

    def remove_extra_disks(self):
        for d in self.disk_list:
            if d.name not in self.current_disks:
                self.disk_list.remove(d)

    def parse_stat_file(self):
        self.stat_file = Common.read_file(self.file_name)
        self.current_disks = []

        for l in self.stat_file:
            if 'loop' not in l[2]: #and 'sda' in l[2]:
                try:
                    self.current_disks.append(l[2])
                    i = self.disk_list.index(Disk(l[2], int(l[4]), int(l[8]), int(l[6]), int(l[10]), self.read_time))
                    self.disk_list[i].update_params(int(l[4]), int(l[8]), int(l[6]), int(l[10]), self.read_time)
                except ValueError:
                    temp_disk = Disk(l[2], int(l[4]), int(l[8]), int(l[6]), int(l[10]), self.read_time)
                    self.disk_list.append(temp_disk)
        self.remove_extra_disks()

    def update_stats(self):
        self.read_time = time.time()
        self.parse_stat_file()

    def get_stats(self):
        self.update_stats()
        print(self.disk_list)
    
    def get_stats_for_gui(self):
        self.update_stats()

        return self.disk_list

# disk_stats = DiskStats()
# disk_stats.get_stats()
# time.sleep(1)
# disk_stats.get_stats()


class MemoryStats:
    def __init__(self, file_name="/proc/meminfo"):
        self.file_name = file_name
        self.read_time = time.time()
        self.memory = Memory()

    def get_total_memory(self):
        return int(self.memory.memory_total)

    def parse_stat_file(self):
        self.stat_file = Common.read_file(self.file_name)
        total_memory, available_memory = 0, 0
        for l in self.stat_file:
            if 'MemTotal' in l[0]:
                total_memory = int(l[1])/1024 # convert to mb
            if 'MemAvailable' in l[0]:
                available_memory = int(l[1])/1024 # convert to mb
            
        self.memory.update_params((total_memory - available_memory), total_memory, self.read_time)

    def update_stats(self):
        self.read_time = time.time()
        self.parse_stat_file()

    def get_stats(self):
        self.update_stats()
        print(self.memory)

    def get_stats_for_gui(self):
        self.update_stats()

        return self.memory.get_utilization()
        
# memory_stats = MemoryStats()
# memory_stats.get_stats()
# time.sleep(1)
# memory_stats.get_stats()


class ProcessStats:
    def __init__(self):
        self.read_time = time.time()
        self.process_list = []
        self.physical_memory_total = None
        self.page_size = None
        self.virtual_memory_total = None
        self.inode_dict = {}
        self.sys_wide_cpu_time = 0

    def get_all_pids(self):
        return self.remove_completed_pids(set([f for f in os.listdir("/proc") if str.isdigit(f)]))

    def set_sys_wide_cpu_time(self, time):
        self.sys_wide_cpu_time = time

    def remove_completed_pids(self, pids):
        pop_list = []
        for i in range(0, len(self.process_list)):
            if self.process_list[i].pid not in pids:
                pop_list.append(self.process_list[i])
        for p in pop_list:
            self.process_list.remove(p)
            
        return pids

    def get_inode_dict(self):
        return self.inode_dict

    def get_inode(self, pid):
        inode = ""
        try:       
            path = "/proc/"+pid+"/fd"
            files_in_path = os.listdir(path)  
            for file in files_in_path: 
                if str.isdigit(file): 
                    file_name = "/proc/" + pid + "/fd/" + file  
                    if (os.path.exists(file_name)):
                        if S_ISSOCK(os.stat(file_name).st_mode):
                            self.inode_dict[str(os.stat(file_name).st_ino)] = pid
                            inode = str(os.stat(file_name).st_ino)
        except Exception as ex:
            print(f"Inode could not be found for { pid }. { ex }")

        return inode

    def read_content(self, pid, stat_file, status_file):
        name = stat_file[0][1].replace("(", "").replace(")", "")
        user_mode = stat_file[0][13]
        sys_mode = stat_file[0][14]
        virtual_memory = stat_file[0][22]
        resident_set_size = stat_file[0][23]
        uid = status_file[8][1]
        user_name = Common.get_user_name(uid)
        inode = self.get_inode(pid)
        try:
            i = self.process_list.index(Process(pid, name, user_name, inode, user_mode, sys_mode, virtual_memory, resident_set_size, self.read_time))
            self.process_list[i].update_params(user_mode, sys_mode, virtual_memory, resident_set_size, self.read_time)
        except ValueError:
            temp_process = Process(pid, name, user_name, inode, user_mode, sys_mode, virtual_memory, resident_set_size, self.read_time)
            self.process_list.append(temp_process)

    def parse_stat_file(self):
        pids = self.get_all_pids()
        
        for pid in pids:
            if os.path.isdir("/proc/" + pid):
                stat_file = Common.read_file("/proc/" + pid + "/stat")
                status_file = Common.read_file("/proc/" + pid + "/status")
                self.read_content(pid, stat_file, status_file)

    def update_stats(self):
        self.read_time = time.time()
        self.parse_stat_file()

    def get_stats(self):
        self.update_stats()
        print(self.process_list)

    def get_page_size(self):
        if self.page_size == None:
            self.page_size = int(subprocess.check_output(["getconf", "PAGE_SIZE"]).decode("utf-8"))

        return self.page_size

    def set_physical_memory_total(self, val_in_mb):
        if self.physical_memory_total == None:
            self.physical_memory_total = (int(val_in_mb) * 1024 * 1024) / self.get_page_size()

    def get_virtual_memory_total(self):
        if self.virtual_memory_total == None:
            arch = subprocess.check_output(["uname", "-m"]).decode("utf-8")
            if "64" in arch:
                self.virtual_memory_total = 2**64
            else:
                self.virtual_memory_total = 2**32

        return self.virtual_memory_total

    def get_stats_for_gui(self):
        self.update_stats()

        return self.process_list
 
# process_stats = ProcessStats()
# process_stats.get_stats()
# time.sleep(1)
# process_stats.get_stats()     
    

class NetworkStats:
    def __init__(self, file_name="/proc/net/dev"):
        self.file_name = file_name
        self.read_time = time.time()
        self.network_list = []
        self.network_bandwidths = {}
    
    def get_network_bandwidth(self, device_name):
        if device_name not in self.network_bandwidths:
            try:
                out = subprocess.check_output(["ethtool", device_name]).decode("utf-8")
                speed = re.findall(r'Speed.*', out)[0].split()[1]
                bandwidth = re.sub(r'\D*','',speed)  #in Mb/s
                self.network_bandwidths[device_name] = int(bandwidth) * 125000 #Mb/s to Bytes/s
            except:
                self.network_bandwidths[device_name] = 0

        return self.network_bandwidths[device_name]

    def parse_stat_file(self):
        self.stat_file = Common.read_file(self.file_name)

        for dev in self.stat_file[2:]:
            name = dev[0][:-1]

            if name != "lo":
                try:
                    i = self.network_list.index(NetworkDevice(name))
                    self.network_list[i].update_params(int(dev[1]), int(dev[8]), self.get_network_bandwidth(name), self.read_time)
                except ValueError:
                    self.network_list.append(NetworkDevice(name, int(dev[1]), int(dev[8]), self.get_network_bandwidth(name), self.read_time))

    def update_stats(self):
        self.read_time = time.time()
        self.parse_stat_file()

    def get_stats(self):
        self.update_stats()
        print(self.network_list)

    def get_stats_for_gui(self):
        self.update_stats()

        return self.network_list

# network_stats = NetworkStats()
# network_stats.get_stats()
# time.sleep(1)
# network_stats.get_stats()


class ConnectionStats:
    def __init__(self, tcp_file_name="/proc/net/tcp", udp_file_name="/proc/net/udp"):
        self.tcp_file_name = tcp_file_name
        self.udp_file_name = udp_file_name
        self.tcp_file = []
        self.udp_file = []
        self.tcp_conns = []
        self.udp_conns = []
        self.inode_dict = {}

    def set_inode_dict(self, inode_dict):
        self.inode_dict = inode_dict

    # need to implement inode_dict      
    def get_program_from_inode(self, inode):
        program = ""
        try:
            if inode in self.inode_dict.keys():
                pid = self.inode_dict[inode]
                if pid:
                    proc_folder_path = "/proc/" + pid + "/comm"
                    if (os.path.exists(proc_folder_path)):
                        procFile = Common.read_file(proc_folder_path)
                        program = procFile[0][0]
            return program
        except Exception as ex:
            proc_folder_path = "/proc/" + pid + "/comm"
            if (os.path.exists(proc_folder_path)):
                procFile = Common.read_file(proc_folder_path)
                program = procFile[0][0]
                print(program)
            print(f"Error figuring out program name from '{ inode }'. {ex}")
            return program

    def get_ip_info(self, hex):
        ip, host_name, port = "", "", ""
        try:
            hex_ip = hex.split(":")[0]
            ip = socket.inet_ntoa(bytes.fromhex(hex_ip))
            port = int(hex.split(":")[1], 16)
            host_name = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            pass
        except Exception as ex: 
            print(f"Error figuring out ip info from '{ hex }'.\nException: { ex }.")
        
        return ip, host_name, port

    def get_established_connections(self):
        count = 0
        for conn in self.tcp_file[1:]:
            if conn[3] == "01":
                count += 1
        
        return count

    def read_content(self, typ="tcp"):
        if typ =="tcp":
            file = self.tcp_file
            connections = self.tcp_conns
        else:
            file = self.udp_file    
            connections = self.udp_conns

        for conn in file[1:]:
            id = conn[0][:-1]
            uid = int(conn[7])
            user_name = Common.get_user_name(uid)

            inode = conn[9]
            program = self.get_program_from_inode(inode)
            source_ip, source_hostname, source_port = self.get_ip_info(conn[1])
            destination_ip, destination_hostname, destination_port = self.get_ip_info(conn[2])
            try:
                i = connections.index(Connection(id))
                connections[i].update_params(uid, user_name, inode, program, 
                    source_hostname, source_ip, source_port, 
                    destination_hostname, destination_ip, destination_port)
            except ValueError:
                connections.append(Connection(id, uid, user_name, inode, program, 
                    source_hostname, source_ip, source_port, 
                    destination_hostname, destination_ip, destination_port))

        return connections

    def parse_stat_file(self):
        self.tcp_file = Common.read_file(self.tcp_file_name)
        self.udp_file = Common.read_file(self.udp_file_name)

        self.tcp_conns = self.read_content("tcp")
        self.udp_conns = self.read_content("udp")
        self.tcp_established_conns = self.get_established_connections()

    def update_stats(self):
        self.parse_stat_file()

    def get_stats(self):
        self.update_stats()
        print(f"TCP Established Connections count: { self.tcp_established_conns }.")
        print(f"TCP Connections: { self.tcp_conns }\nUDP Connections: { self.udp_conns }")

    def get_stats_for_gui(self):
        self.update_stats()

        return self.tcp_established_conns, self.tcp_conns, self.udp_conns

# connection_stats = ConnectionStats()
# connection_stats.get_stats()
# time.sleep(1)
# connection_stats.get_stats()