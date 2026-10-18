# 免費代理 IP 數量統計

統計時間：2026-10-18 21:25～21:30（UTC+8，即 13:25～13:30 UTC）
統計方式：直接抓取各網址當下回傳的頁面／API／清單檔，解析其中的 IP:端口 條目。

| # | 來源網址 | 當下數量 | 說明 |
|---|----------|---------:|------|
| 1 | https://www.vpngate.net/cn/ | 100 | 100 台 VPN Gate 公開伺服器（OpenVPN／L2TP／SSTP，屬於 VPN 而非 HTTP 代理） |
| 2 | https://proxy.scdn.io/ | 31,171 | API 共 312 頁 × 100 筆，末頁 71 筆（`get_proxies.php`） |
| 3 | https://www.zdaye.com/free/ | 574 | 頁面標示「當前篩選條件下共 574 個免費代理IP」，每頁 20 筆 |
| 4 | https://fineproxy.org/cn/free-proxies/asia/china/ | 52 | 頁面 `data-total="52"`，解析出 52 筆 |
| 5 | https://proxy5.net/cn/free-proxy | 17,837 | 頁面標示「在線代理：17837」，JSON 清單同為 17,837 筆 |
| 6 | https://fineproxy.org/cn/free-proxies/asia/cambodia/ | 1 | `data-total="1"` |
| 7 | https://api.openproxylist.xyz/ | 21,684 | HTTP 6,025 + HTTPS 5,735 + SOCKS4 4,674 + SOCKS5 5,250；去重後 13,882 個 IP:端口、9,889 個獨立 IP |
| 8 | https://fineproxy.org/cn/free-proxies/oceania/ | 0 | 頁面顯示「沒有符合這些篩選條件的代理」 |
| 9 | https://fineproxy.org/cn/free-proxies/asia/hong-kong/ | 0 | 同上，目前無在線代理 |
| 10 | https://fineproxy.org/cn/free-proxies/asia/pakistan/ | 22 | `data-total="22"` |

## 合計

- **各站列出的條目總和：71,441 筆**（含同一 IP 不同端口、不同協議的重複計算）。
- 可完整去重比對的清單（proxy5 + openproxylist + fineproxy）：**29,558 個唯一 IP:端口**，換算為 **15,823 個獨立 IP**。
- 再加上 vpngate 的 100 個 IP（與上述代理清單無重疊）：**15,923 個獨立 IP**。
- scdn.io 的 31,171 筆與 zdaye 的 574 筆因站方限流，未能逐頁抓取去重；若直接相加，唯一 IP:端口數的上限為 **61,303**，實際會更低（scdn 與 openproxylist 有大量重疊）。

## 注意事項

1. 這些網站都是即時更新的免費代理池，數量每分鐘都在變動，以上僅為統計當下的快照。
2. 「條目數」不等於「可用代理數」：同一 IP 可能有多個端口／協議，且免費代理的失效率通常很高。
3. vpngate 提供的是 VPN 伺服器，並非 HTTP／SOCKS 代理，是否計入總數需視用途而定。
