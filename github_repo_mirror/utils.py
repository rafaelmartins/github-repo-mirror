from ipaddress import IPv4Address, IPv4Network


def request_allowed(remote_addr, allowed_network, debug=False):
    if remote_addr is None:
        raise RuntimeError('Failed to find remote IP address')
    # IPv6 unsupported for now
    ip = IPv4Address(remote_addr)
    if debug and ip.is_private:
        return True
    network = IPv4Network(allowed_network)
    return ip in network

