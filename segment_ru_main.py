from ipaddress import IPv4Address, IPv4Network, collapse_addresses, summarize_address_range
import json
import requests


def get_ripe_ip(countrycode):
    url = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=' + countrycode
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


country_code = input("Введите код страны: ") or "RU"
prefixes = get_ripe_ip(country_code)
data = [str(p) for p in prefixes]
with open("routes_cli_aggregate.txt", "w") as file:
    routes = [IPv4Network(prefix) for prefix in data]
    aggr_routes = collapse_addresses(routes)
    for aggr_route in aggr_routes:
        route = ["ip route", str(aggr_route.network_address), str(aggr_route.netmask), "185.155.17.1 ISP\n"]
        file.write(" ".join(route))
