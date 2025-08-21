import ipaddress
def ip_whitelisted(ip, cidrs):
    try:
        ip_obj = ipaddress.ip_address(ip)
        for c in cidrs:
            if ip_obj in ipaddress.ip_network(c, strict=False):
                return True
    except Exception:
        pass
    return False
