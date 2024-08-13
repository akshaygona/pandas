import re
import netaddr
import pandas as pd
from bisect import bisect

ips = pd.read_csv("ip2location.csv")

def lookup_region(address):
    address = re.sub(r"([a-zA-Z])", "0", address)
    pattern = r'(0+)$'
    replacement = '0'
    address = re.sub(pattern, replacement, address)
    intAddress = int(netaddr.IPAddress(address))
    idx = bisect(ips["low"], intAddress)
    return ips.iloc[idx-1]["region"]

class Filing:
    def __init__(self, html):
        self.dates = []
        for i in re.findall(r"((19|20)\d{2}-(0\d|1[0-2])-(0[1-9]|1\d|2\d|3[0-1]))", html):
            self.dates.append(i[0])
        sics = re.findall(r"SIC=(\d+)", html)
        if len(sics) == 0:
            self.sic = None
        else:
            self.sic = int(sics[0])
        self.addresses = []
        for addr_html in re.findall(r"\<div class=\"mailer\"\>([\s\S]+?)\</div\>", html):
            lines = []
            for line in re.findall(r"\<span class=\"mailerAddress\"\>([\s\S]+?)\</span\>", addr_html):
                lines.append(line.strip())
            if len(lines) > 0:
                self.addresses.append("\n".join(lines))
        
    def state(self):
        for address in self.addresses:
            regex = re.findall(r"\s([A-Z]{2})\s\d{5}", address)
            if len(regex) > 0:
                return regex[0]
        return None