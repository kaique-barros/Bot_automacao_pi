import capsolver

proxy = {
    "user": "hvy43092ouavzjg-country-br",
    "pass": "8ft7a2mr3mfjp8p",
    "host": "rp.scrapegw.com",
    "port": "6060"
}

PROXY_CONNECTION = f"{proxy['host']}:{proxy['port']}:{proxy['user']}:{proxy['pass']}"

capsolver.api_key = "CAP-D38F9278056E5453E567FB2115F9D2FF89C61B09C5F64FDBE74D1B76D2A81521"

GGMAX_SITE_KEY = "0x4AAAAAAADnPIDROrmt1Wwj" 
PAGE_URL = "https://ggmax.com.br"

solution = capsolver.solve({
    "type": "AntiCloudflareTask",
    "websiteURL": PAGE_URL,
    "proxy": PROXY_CONNECTION
})

print(solution)
print(solution.get("token"), None)