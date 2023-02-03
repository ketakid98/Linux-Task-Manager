import json

from .common import Common


class IntervalVal: 
    def __init__(self, name, val=0, read_time=0):
        self.name = name
        self.val = { "prev":0, "curr": val }
        self.read_time = { "prev":0, "curr": read_time }

    def __eq__(self, other): 
        if not isinstance(other, IntervalVal):
            return NotImplemented

        return self.name == other.name

    def __str__(self):
        utils = self.get_utilization()

        return f"""\nName: { self.name }
            \n\tVal: prev = { self.val['prev'] }, curr = {self.val['curr']}
            \n\tRead Time: prev = { self.read_time["prev"] }, curr = { self.read_time['curr'] }
            \n\tInterval Value: { utils["interval_val"] }"""

    def __repr__(self):
        return str(self)

    def update_params(self, val, read_time):
        self.val["prev"] = self.val["curr"]
        self.read_time["prev"] = self.read_time["curr"]
        self.val["curr"] = val
        self.read_time["curr"] = read_time

    def get_utilization(self):        
        return {
            "name": self.name,
            "interval_val": Common.round2(Common.get_interval_vals(self.val["prev"], self.val["curr"], (self.read_time["curr"] - self.read_time["prev"])))
        }
 
    
class CPU:
    def __init__(self, name, user_mode=0, sys_mode=0, idle_mode=0, read_time=0):
        self.name = name
        self.user_mode = { "prev":0, "curr": user_mode }
        self.sys_mode = { "prev":0, "curr": sys_mode }
        self.idle_mode = { "prev":0, "curr": idle_mode } 
        self.read_time = { "prev":0, "curr": read_time }
        self.sys_wide_time = 0

    def __eq__(self, other): 
        if not isinstance(other, CPU):
            return NotImplemented

        return self.name == other.name

    def __str__(self):
        utils = self.get_utilization()

        return f"""\nSystem Wide Time: { self.sys_wide_time }\nRead Time: prev = { self.read_time['prev'] }, 
            curr = { self.read_time['curr'] }\nCPU Name: { self.name }\n\tUser Mode Utilization: 
            prev = { self.user_mode['prev'] }, curr = { self.user_mode['curr'] }, 
            percent = { utils["percent_user_util"] }\n\tSystem Mode Utilization: prev = { self.sys_mode['prev'] }, 
            curr = { self.sys_mode['curr'] }, percent = { utils["percent_sys_util"] }\n\t
            Overall Utilization: { utils["percent_overall_util"] }"""

    def __repr__(self):
        return str(self)

    def to_json(self):
        return json.dumps(self.get_utilization())
    
    def set_sys_wide_time(self):
        self.delta_user_mode = int(self.user_mode["curr"]) - int(self.user_mode["prev"])
        self.delta_sys_mode = int(self.sys_mode["curr"]) - int(self.sys_mode["prev"])
        self.delta_idle_mode = int(self.idle_mode["curr"]) - int(self.idle_mode["prev"])
        self.sys_wide_time =  self.delta_user_mode + self.delta_sys_mode + self.delta_idle_mode

    def update_params(self, user_mode, sys_mode, idle_mode, read_time):
        self.user_mode["prev"] = self.user_mode["curr"]
        self.sys_mode["prev"] = self.sys_mode["curr"]
        self.idle_mode["prev"] = self.idle_mode["curr"]
        self.read_time["prev"] = self.read_time["curr"]
        self.user_mode["curr"] = user_mode
        self.sys_mode["curr"] = sys_mode
        self.idle_mode["curr"] = idle_mode
        self.read_time["curr"] = read_time
        self.set_sys_wide_time()

    def get_utilization(self):
        percent_user_util, percent_sys_util, percent_overall_util = 0.0, 0.0, 0.0
        if (self.sys_wide_time!=0):
            percent_user_util = (self.delta_user_mode / self.sys_wide_time) * 100
            percent_sys_util = (self.delta_sys_mode / self.sys_wide_time) * 100
            percent_overall_util = ((self.delta_sys_mode + self.delta_user_mode) / self.sys_wide_time) * 100

        return {
            "name": self.name,
            "percent_user_util": Common.round2(percent_user_util), 
            "percent_sys_util": Common.round2(percent_sys_util), 
            "percent_overall_util": Common.round2(percent_overall_util)
        }

class Memory:
    def __init__(self, memory_used=0, memory_total=0, read_time=0):
        self.memory_used = { "prev":0, "curr": memory_used }
        self.memory_total = memory_total
        self.read_time = { "prev":0, "curr": read_time }

    def __eq__(self, other): 
        if not isinstance(other, CPU):
            return NotImplemented

        return self.name == other.name

    def __str__(self):
        utils = self.get_utilization()

        return f"""\nRead Time: prev = { self.read_time['prev'] }, curr = { self.read_time['curr'] }
            \nMemory Total: { self.memory_total }
            \nMemory Used: prev = { self.memory_used['prev'] }, curr = { self.memory_used['curr'] }
            \n\tMemory Utilization = { utils["memory_util"] }%"""

    def __repr__(self):
        return str(self)

    def to_json(self):
        return json.dumps(self.get_utilization())

    def update_params(self, memory_used, memory_total, read_time):
        self.memory_used["prev"] = self.memory_used["curr"]
        self.read_time["prev"] = self.read_time["curr"]
        self.memory_used["curr"] = memory_used
        self.memory_total = memory_total
        self.read_time["curr"] = read_time

    def get_utilization(self):
        avg_memory_used = (float(self.memory_used["curr"] + self.memory_used["prev"]) / 2)
        memory_util = (avg_memory_used / self.memory_total) * 100

        return {
            "memory_util": Common.round2(memory_util),
            "memory_total": Common.round2(self.memory_total),
            "memory_used": Common.round2(avg_memory_used)
        }


class Disk:
    def __init__(self, name, disk_read, disk_write, block_read, block_write, read_time):
        self.name = name
        self.disk_read = { "prev":0, "curr": disk_read }
        self.disk_write = { "prev":0, "curr": disk_write }
        self.block_read = {"prev":0, "curr": block_read }
        self.block_write = {"prev":0, "curr": block_write }
        self.read_time = { "prev": 0, "curr": read_time }

    def __eq__(self, other): 
        if not isinstance(other, Disk):
            return NotImplemented

        return self.name == other.name

    def __str__(self):
        utils = self.get_utilization()

        return f"""\nDisk Name: { self.name }
            \n\tDisk Read: prev = { self.disk_read['prev'] }, curr = {self.disk_read['curr']}
            \n\tDisk Write: prev = { self.disk_write["prev"] }, curr = { self.disk_write['curr'] }
            \n\tBlock Read: prev = { self.block_read["prev"] }, curr = { self.block_read['curr'] }
            \n\tBlock Write: prev = { self.block_write["prev"] }, curr = { self.block_write['curr'] }
            \n\tRead Time: prev = { self.read_time["prev"] }, curr = { self.read_time['curr'] }
            \n\tDisk Read Speed: { utils["disk_read_speed"] }
            \n\tDisk Write Speed: { utils["disk_write_speed"] }
            \n\tBlock Read Speed: { utils["block_read_speed"] }
            \n\tBlock Write Speed: { utils["block_write_speed"] }"""

    def __repr__(self):
        return str(self) 
        
    def to_json(self):     
        return json.dumps(self.get_utilization())

    def update_params(self, disk_read, disk_write, block_read, block_write, read_time):
        self.disk_read["prev"] = self.disk_read["curr"]
        self.disk_write["prev"] = self.disk_write["curr"]
        self.block_read["prev"] = self.block_read["curr"]
        self.block_write["prev"] = self.block_write["curr"]
        self.read_time["prev"] = self.read_time["curr"]
        self.disk_read["curr"] = disk_read
        self.disk_write["curr"] = disk_write
        self.block_write["curr"] = block_write
        self.block_read["curr"] = block_read
        self.read_time["curr"] = read_time

    def get_utilization(self):
        interval = (self.read_time["curr"] - self.read_time["prev"])
        disk_read_speed = Common.get_interval_vals(self.disk_read["prev"], self.disk_read["curr"], interval)
        disk_write_speed = Common.get_interval_vals(self.disk_write["prev"], self.disk_write["curr"], interval)
        block_read_speed = Common.get_interval_vals(self.block_read["prev"], self.block_read["curr"], interval)
        block_write_speed = Common.get_interval_vals(self.block_write["prev"], self.block_write["curr"], interval)

        return  {
            "name": self.name,
            "disk_read_speed": Common.round2(disk_read_speed),
            "disk_write_speed": Common.round2(disk_write_speed),
            "block_read_speed": Common.round2(block_read_speed),
            "block_write_speed": Common.round2(block_write_speed)
        } 


class Process:
    def __init__(self, pid, name, user_name, inode_number, user_mode=0, sys_mode=0, virtual_memory=0, resident_set_size=0, read_time=0):
        self.pid = pid
        self.name = name
        self.user_name = user_name
        self.inode_number = inode_number
        self.user_mode = { "prev":0, "curr": user_mode }
        self.sys_mode = { "prev":0, "curr": sys_mode }
        self.virtual_memory = { "prev":0, "curr": virtual_memory }
        self.resident_set_size = { "prev":0, "curr": resident_set_size }
        self.read_time = { "prev":0, "curr": read_time }

    def __eq__(self, other): 
        if not isinstance(other, Process):
            return NotImplemented

        return self.pid == other.pid

    def __str__(self):
        return f"""\Process Name: { self.name }, PID: { self. pid }, INode: { self.inode_number }, 
            User Name: { self.user_name }
            \n\tUser Mode: prev = { self.user_mode['prev'] }, curr = { self.user_mode['curr'] }
            \n\tSystem Mode: prev = { self.sys_mode['prev'] }, curr = { self.sys_mode['curr'] }
            \n\tUser Mode: prev = { self.user_mode['prev'] }, curr = { self.user_mode['curr'] }
            \n\tVirtual Memory: prev = { self.virtual_memory['prev'] }, curr = { self.virtual_memory['curr'] }
            \n\tResident Set Size: prev = { self.resident_set_size['prev'] }, curr = { self.resident_set_size['curr'] }
            \n\tRead Time: prev = { self.read_time['prev'] }, curr = { self.read_time['curr'] }"""

    def __repr__(self):
        return str(self)
        
    def to_json(self):     
        return json.dumps(self.get_utilization())

    def get_cpu_utilization(self, system_wide_time):
        delta_user_mode = int(self.user_mode["curr"]) - int(self.user_mode["prev"])
        delta_sys_mode = int(self.sys_mode["curr"]) - int(self.sys_mode["prev"])

        percent_user_util, percent_sys_util, percent_overall_util = 0, 0, 0
        if system_wide_time != 0:
            percent_user_util = (delta_user_mode / system_wide_time) * 100
            percent_sys_util = (delta_sys_mode / system_wide_time) * 100
            percent_overall_util = ((delta_user_mode + delta_sys_mode) / system_wide_time) * 100

        return {
            "percent_user_util": Common.round2(percent_user_util), 
            "percent_sys_util": Common.round2(percent_sys_util), 
            "percent_overall_util": Common.round2(percent_overall_util)
        }

    def get_virtual_memory_utilization(self, type="normal"):
        """
        return virutal memory in bytes/sec
        """
        interval = self.read_time["curr"] - self.read_time["prev"]
        if type=="normal":
            delta_virtual_memory = float(self.virtual_memory["curr"]) - float(self.virtual_memory["prev"])
        else: # avg
            delta_virtual_memory = (float(self.virtual_memory["curr"]) + float(self.virtual_memory["prev"])) / 2
        if interval != 0:
            return Common.round2(delta_virtual_memory / interval)
        return 0
    
    def get_physical_memory_utilization(self, physical_memory_total):
        if physical_memory_total != 0:
            #delta_phyMem = int(self.rss["curr"]) - int(self.rss["prev"]) 
            return Common.round2((float(self.resident_set_size['curr']) / float(physical_memory_total)) * 100)
        return 0

    def update_params(self, user_mode, sys_mode, virtual_memory, resident_set_size, read_time):
        self.user_mode["prev"] = self.user_mode["curr"]
        self.sys_mode["prev"] = self.sys_mode["curr"]
        self.virtual_memory["prev"] = self.virtual_memory["curr"]
        self.resident_set_size["prev"] = self.resident_set_size["curr"]
        self.read_time["prev"] = self.read_time["curr"]
        self.user_mode["curr"] = user_mode
        self.sys_mode["curr"] = sys_mode
        self.resident_set_size["curr"] = resident_set_size
        self.virtual_memory["curr"] = virtual_memory
        self.read_time["curr"] = read_time

    def get_utilization(self, system_wide_time, physical_memory_total):
        utils = self.get_cpu_utilization(system_wide_time)
        utils["pid"] = self.pid
        utils["name"] = self.name
        utils["user_name"] = self.user_name
        utils["inode"] = self.inode_number
        utils["virtual_memory_utilization"] = self.get_virtual_memory_utilization()
        utils["avg_virtual_memory_utilization"] = self.get_virtual_memory_utilization("avg")
        utils["physical_memory_utilization"] = self.get_physical_memory_utilization(physical_memory_total)

        return utils


class NetworkDevice:
    def __init__(self, name, bytes_in=0, bytes_out=0, network_bandwidth=0, read_time=0):
        self.name = name
        self.bytes_in = { "prev": 0, "curr": bytes_in }
        self.bytes_out = { "prev": 0, "curr": bytes_out }
        self.network_bandwidth = { "prev": 0, "curr": network_bandwidth }
        self.read_time = { "prev": 0, "curr": read_time }

    def __eq__(self, other): 
        if not isinstance(other, NetworkDevice):
            return NotImplemented

        return self.name == other.name

    def __str__(self):
        utils = self.get_utilization()

        return f"""\nNetwork Name: { self.name }
            \n\tBytes in: prev = { self.bytes_in['prev'] }, curr = {self.bytes_in['curr']}
            \n\tBytes out: prev = { self.bytes_out["prev"] }, curr = { self.bytes_out['curr'] }
            \n\tNetwork Bandwidth Read: prev = { self.network_bandwidth["prev"] }, curr = { self.network_bandwidth['curr'] }
            \n\tRead Time: prev = { self.read_time["prev"] }, curr = { self.read_time['curr'] }
            \n\tAverage Network Utilization: { utils["avg_network_util"] }b/s
            \n\tCurrent Network Utilization: { utils["current_network_util"] }b/s"""

    def __repr__(self):
        return str(self) 
        
    def to_json(self):     
        return json.dumps(self.get_utilization())

    def update_params(self, bytes_in, bytes_out, network_bandwidth, read_time):
        self.bytes_in["prev"] = self.bytes_in["curr"]
        self.bytes_out["prev"] = self.bytes_out["curr"]
        self.network_bandwidth["prev"] = self.network_bandwidth["curr"]
        self.read_time["prev"] = self.read_time["curr"]
        self.bytes_in["curr"] = bytes_in
        self.bytes_out["curr"] = bytes_out
        self.network_bandwidth["curr"] = network_bandwidth
        self.read_time["curr"] = read_time

    def get_avg_network_utilization(self):
        interval = self.read_time['curr'] - self.read_time['prev']
        if interval != 0:
            delta_bytes_in = self.bytes_in['curr'] - self.bytes_out['prev']
            delta_bytes_out = self.bytes_out['curr'] - self.bytes_out['prev']
            return Common.round2((delta_bytes_in + delta_bytes_out) / interval)
        return 0

    def get_network_utilization(self):
        if self.network_bandwidth['curr'] == 0:
            return 0

        interval = self.read_time['curr'] - self.read_time['prev']
        if interval != 0:
            bytes_in_sec = self.bytes_in['curr'] - self.bytes_in['prev']
            bytes_out_sec = self.bytes_out['curr'] - self.bytes_out['prev']
            avg_network_bandwidth = (self.network_bandwidth['curr'] + self.network_bandwidth['prev']) / 2
            if avg_network_bandwidth != 0:
                return Common.round2(((bytes_in_sec + bytes_out_sec) / avg_network_bandwidth) * 100)

        return 0

    def get_utilization(self):
        avg_network_util = self.get_avg_network_utilization()
        network_util = self.get_network_utilization()

        return  {
            "name": self.name,
            "avg_network_util": avg_network_util,
            "current_network_util": network_util,
            "bandwidth": self.network_bandwidth['curr'] - self.network_bandwidth['prev'],
            "rec": self.bytes_in['curr'] - self.bytes_in['prev'],
            "sent": self.bytes_out['curr'] - self.bytes_out['prev']
        } 


class Connection:
    def __init__(self, id, uid=-1, user_name="", inode=-1, program="", 
                    source_hostname="", source_ip="", source_port="", 
                    destination_hostname="", destination_ip="", destination_port=""):
        self.id = id
        self.uid = uid
        self.user_name = user_name
        self.inode = inode
        self.program = program
        self.source_hostname = source_hostname
        self.source_ip = source_ip
        self.source_port = source_port
        self.destination_hostname = destination_hostname
        self.destination_ip = destination_ip
        self.destination_port = destination_port

    def __eq__(self, other): 
        if not isinstance(other, Connection):
            return NotImplemented
 
        return self.id == other.id

    def __str__(self):
        return f"""\nConnection Id: { self.id }, User Name: { self.user_name },
            User Id: { self.uid }, Program: { self.program }, Inode: {self.inode }
            \nSource: Host Name = { self.source_hostname }, IP = { self.source_ip } & Port = { self.source_port }
            \nDestination: Host Name = { self.destination_hostname }, IP = { self.destination_ip } & Port = { self.destination_port }"""

    def __repr__(self):
        return str(self) 
        
    def to_json(self):     
        return json.dumps(self.get_utilization())

    def update_params(self, uid, user_name, inode, program, source_hostname, source_ip, source_port, 
        destination_hostname, destination_ip, destination_port):
        self.uid = uid
        self.inode = inode
        self.user_name = user_name
        self.program = program
        self.source_hostname = source_hostname
        self.source_ip = source_ip
        self.source_port = source_port
        self.destination_hostname = destination_hostname
        self.destination_ip = destination_ip
        self.destination_port = destination_port

    def get_utilization(self):
        return  {
            "id": self.id,
            "uid": self.uid,
            "inode": self.inode,
            "user_name": self.user_name,
            "program": self.program,
            "source_hostname": self.source_hostname,
            "source_ip": self.source_ip,
            "source_port": self.source_port,
            "destination_hostname": self.destination_hostname,
            "destination_ip": self.destination_ip,
            "destination_port": self.destination_port
        }

