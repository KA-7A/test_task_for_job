class hostInfo(object):
    def __init__(self):
        self.osName = "Undefined"
        self.IPadress = ""
        self.openPorts = []
        self.filteredPorts = []
        self.isWarning = False

        pass

    def setWarning(self, state):
        self.isWarning = state

    def setOSname(self, name):
        self.osName = name

    def setIPadress(self, addr):
        self.IPadress = addr

    def addOpenPort(self, port):
        self.openPorts.append(port)

    def addFilteredPort(self, port):
        self.filteredPorts.append(port)

    def getOSname(self):
        return self.osName

    def getIPadress(self):
        return self.IPadress

    def getOpenPorts(self):
        return self.openPorts

    def getFilteredPorts(self):
        return self.filteredPorts

    def getWarning(self):
        return self.isWarning

    def getInfo(self):
        warning_port = []
        with open('./warning_port.txt', 'r') as f:
            for eachline in f:
                warning_port.append(int(eachline))
        message = ""
        message += "========================\n"
        message += "Host: " + self.getIPadress() + "\n"
        if self.getOSname() != 'Undefined':
            message += "OS:  "  + self.getOSname()   + "\n"
        if (len(self.getOpenPorts())):
            message += "Open ports (" + str(len(self.getOpenPorts())) + "): \n"
            for j in self.getOpenPorts():
                if int(j) in warning_port:
                    message += "&#128308;"
                    self.setWarning(True)
                message += str(j) + "\n"
        if (len(self.getFilteredPorts())):
            message += "Filtered ports (" + str(len(self.getFilteredPorts())) + "): "
            for j in self.getFilteredPorts():
                message += str(j) + "\n"
        message += "========================\n"
        return message
