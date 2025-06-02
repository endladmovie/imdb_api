import itertools

with open("proxy.txt") as f:
    proxy_list = [line.strip() for line in f if line.strip()]
proxy_cycle = itertools.cycle(proxy_list)

def get_next_proxy():
    proxy = next(proxy_cycle)
    return {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
