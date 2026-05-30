## GitHub Copilot Chat

- Extension: 0.48.1 (prod)
- VS Code: 1.120.0 (0958016b2af9f09bb4257e0df4a95e2f90590f9f)
- OS: win32 10.0.26200 x64
- GitHub Account: yekraztv-gif

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "http.useLocalProxyConfiguration": false,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: 140.82.121.5 (10 ms)
- DNS ipv6 Lookup: Error (4 ms): getaddrinfo ENOTFOUND api.github.com
- Proxy URL: http://127.0.0.1:10808 (4 ms)
- Proxy Connection: 200 Connection established (16 ms)
- Electron fetch (configured): HTTP 200 (4682 ms)
- Node.js https: timed out after 10 seconds
- Node.js fetch: HTTP 200 (7765 ms)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: 140.82.113.21 (19 ms)
- DNS ipv6 Lookup: Error (5 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- Proxy URL: None (0 ms)
- Electron fetch (configured): HTTP 200 (8379 ms)
- Node.js https: HTTP 200 (7388 ms)
- Node.js fetch: timed out after 10 seconds

Connecting to https://copilot-proxy.githubusercontent.com/_ping:
- DNS ipv4 Lookup: 20.250.119.64 (4 ms)
- DNS ipv6 Lookup: Error (4 ms): getaddrinfo ENOTFOUND copilot-proxy.githubusercontent.com
- Proxy URL: None (1 ms)
- Electron fetch (configured): timed out after 10 seconds
- Node.js https: timed out after 10 seconds
- Node.js fetch: 