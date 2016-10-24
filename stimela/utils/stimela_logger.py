### Stimela logging classes
import time

class Container(object):

    def __init__(self, name):
        
        self.name = name

        with open(name) as std:
            lines = std.readlines()

        self.lines = lines
        self.num = len(lines)


    def add(self, cont, pid):
        
        name = cont["Name"][1:]
        cid = cont["Id"][:16]
        uptime = "00:00:00"
        status = cont["State"]["Status"]

        line = "%(name)s %(cid)s %(uptime)s %(pid)s %(status)s\n"%locals()

        self.lines.append(line)


    def rm(self, name):
        
        for line in self.lines:
            _name = line.split()[0]
            if name == _name:
                self.lines.remove(line)
                break


    def update(self, cont, uptime):
        name = cont["Name"]
        status = cont["State"]["Status"]

        for line in self.lines:
            _name, cid, _, pid, _status = line.split()

            if name == _name:
                self.lines.remove(line)
                _line = "%(name)s %(cid)s %(uptime)s %(pid)s %(status)s\n"%locals()
                self.lines.append(_line)
                break

        return True


    def write(self):
        with open(self.name, "w") as std:
            std.write( "".join(self.lines) )


    def display(self):

        print("{:<48} {:<24} {:<24} {:<24} {:>12}".format("CONTAINER", "ID", "UP TIME", "PID", "STATUS") )

        for line in self.lines:
            try:
                cont, _id, uptime, pid, status = line.split()
                print("{:<48} {:<24} {:<24} {:<24} {:>12}".format(cont, _id, uptime, pid, status) )
            except ValueError:
                pass

    def clear(self):
        with open(self.name, "w") as std:
            return



class Image(object):
    def __init__(self, name):
        
        self.name = name

        with open(name) as std:
            lines = std.readlines()

        self.lines = lines
        self.num = len(lines)


    def add(self, image):
        
        name = image["name"]
        if len(name.split(":")) == 2:
            name, tag = name.split(":")
        else:
            tag = image.get("tag", "latest")

        date = "{:d}/{:d}/{:d}-{:d}:{:d}:{:d}".format(*time.localtime()[:6])

        line = "%(name)s %(tag)s %(date)s\n"%locals()

        self.lines.append(line)

    def find(self, name, tag=None):

        for line in self.lines:
            _name, _tag = line.split()[:2]
            if name==_name and tag==_tag:
                return line

            nn = name.split(":")
            if len(nn)==2:
                name, tag = nn
                if name==_name and tag==_tag:
                    return line

        return False


    def rm(self, name, tag):
        found = self.find(name, tag)
        if found:
            self.remove(found)


    def write(self):
        with open(self.name, "w") as std:
            std.write( "".join(self.lines) )


    def display(self):

        print("{:<48} {:<32} {:<12}".format("IMAGE", "TAG", "TIME STAMP") )

        for line in self.lines:
            try:
                image, tag, date = line.split()
                print("{:<48} {:<32} {:<12}".format(image, tag, date) )
            except ValueError:
                pass


    def clear(self):
        with open(self.name, "w") as std:
            return



class Process(object):
    def __init__(self, name):
        
        self.name = name

        with open(name) as std:
            lines = std.readlines()

        self.lines = lines
        self.num = len(lines)


    def add(self, proc):
        
        name = proc["name"]
        date = proc["date"]
        pid = proc["pid"]

        line = "%(name)s %(date)s %(pid)s\n"%locals()
        self.lines.append(line)


    def find(self, pid):
        
        for line in self.lines:
            _pid = line.split()[-1]
            if int(_pid)==pid:
                return line

        return False


    def rm(self, pid):
        line = self.find(pid)
        if line:
            self.lines.remove(line)

    def write(self):
        with open(self.name, "w") as std:
            std.write( "".join(self.lines) )


    def display(self):

        print("{:<48} {:<32} {:<12}".format("PROCESS", "TIME STAMP", "PID") )

        for line in self.lines:
            try:
                image, tag, date = line.split()
                print("{:<48} {:<32} {:<12}".format(image, tag, date) )
            except ValueError:
                pass


    def clear(self):
        with open(self.name, "w") as std:
            return

