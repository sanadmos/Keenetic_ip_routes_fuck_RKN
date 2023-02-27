import re
import ipaddress
from aggregate_prefixes import aggregate_prefixes

def test_octet (acl_octet, acl_wildcard_octet):
    matches = []
    if (acl_wildcard_octet == 0):
        matches.append(acl_octet)
        return matches
    else:
        for test_octet in range(0,256):
            test_result = test_octet | acl_wildcard_octet
            acl_result  = acl_octet | acl_wildcard_octet
            if acl_result == test_result:
                matches.append(test_octet)
        return matches

def wildcard_calculation(network, wildcard):
    potential_matches = []
    acl_address_octets = list(map(int, network.split('.')))
    acl_mask_octets = list(map(int, wildcard.split('.')))

    matches_octet_1_ref = test_octet(acl_address_octets[0], acl_mask_octets[0])
    matches_octet_2_ref = test_octet(acl_address_octets[1], acl_mask_octets[1])
    matches_octet_3_ref = test_octet(acl_address_octets[2], acl_mask_octets[2])
    matches_octet_4_ref = test_octet(acl_address_octets[3], acl_mask_octets[3])

    for n1 in matches_octet_1_ref:
        for n2 in matches_octet_2_ref:
            for n3 in matches_octet_3_ref:
                for n4 in matches_octet_4_ref:
                    potential_matches.append(str(n1)+'.'+str(n2)+'.'+str(n3)+'.'+str(n4))
    ip = []
    for m in potential_matches:
        ip.append(ipaddress.ip_address(m))
    out = list(ipaddress.collapse_addresses(ip))
    return out

routes = []
with open ("list_ip.lst", "r") as s_file:
    data = s_file.readlines()
with open ("routes_cli.txt", "w") as d_file:
    for prefix in data:
        regexp = r'^(?P<ip_address>(?:[0-9]{1,3}\.){3}(?:[0-9]{1,3}))(?:\s+)?(?:\/)?(?:\s+)?(?P<ip_mask>(?:(?:255|254|252|248|240|224|192|128|0)\.){3}(?:255|254|252|248|240|224|192|128|0)|\d{1,2})$'
        ip_address, ip_mask = re.match(regexp, prefix).groups()
        ip_object = ipaddress.IPv4Interface(ip_address + "/" + ip_mask)
        network = ip_object.network.network_address
        mask = ip_object.netmask
        #route = f"route ADD {network} MASK {mask} 100.68.0.1\n"
        route = f"ip route {network} {mask} 100.68.0.1 ISP\n"
        routes.append(str(ip_object))
        d_file.write(route)

with open("routes_cli_aggr.txt", "w") as aggr_cli_file:
    aggr_routes = aggregate_prefixes(routes)
    for aggr_route in aggr_routes:
        aggr_cli_file.write("ip route " + str(aggr_route.network_address) + " " + str(aggr_route.netmask) + " 100.68.0.1 ISP\n")


# route ADD 157.0.0.0 MASK 255.0.0.0 157.55.80.1