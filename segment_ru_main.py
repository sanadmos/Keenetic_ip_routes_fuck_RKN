import re
import ipaddress
from ipaddress import IPv4Address, IPv4Network, ip_address, summarize_address_range
from aggregate_prefixes import aggregate_prefixes
import json
import requests

def get_ripe_ip(country_code):
    url = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=' + country_code
    ripe_ip = json.loads(requests.get(url, verify=False).content)['data']['resources']['ipv4']
    networks = []
    for record in ripe_ip:
        if record.find('-') > -1:
            ips = record.split('-')
            ipaddr = list(summarize_address_range(IPv4Address(ips[0]), IPv4Address(ips[1])))
        else:
            ipaddr = [IPv4Network(record)]
        networks.extend(ipaddr)
    return networks
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

if __name__ == "__main__":
    country_code = input("Введите код страны: ") or "RU"
    prefixes = get_ripe_ip(country_code)
    data = [str(p) for p in prefixes]
    routes = []
    with open("routes_cli_aggregate.txt", "w") as file:
        regexp = r'^(?P<ip_address>(?:[0-9]{1,3}\.){3}(?:[0-9]{1,3}))(?:\s+)?(?:\/)?(?:\s+)?(?P<ip_mask>(?:(?:255|254|252|248|240|224|192|128|0)\.){3}(?:255|254|252|248|240|224|192|128|0)|\d{1,2})$'
        routes = []
        for prefix in data:
            ip_address, ip_mask = re.match(regexp, prefix).groups()
            ip_object = ipaddress.IPv4Interface(ip_address + "/" + ip_mask)
            routes.append(ip_object)
        aggr_routes = aggregate_prefixes(routes)
        for aggr_route in aggr_routes:
            file.write("ip route " + str(aggr_route.network_address) + " " + str(aggr_route.netmask) + " 100.68.0.1 ISP\n")
