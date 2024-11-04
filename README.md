# Unichain Node

![image](logo.png)

This repository contains the relevant configuration to run your own node on the Unichain network.

### Troubleshooting

If you encounter problems with your node, please open a [GitHub issue](https://github.com/Uniswap/unichain-node/issues)

### Supported Networks

| Network           | Status |
| ----------------- | ------ |
| Testnet (Sepolia) | ✅     |

### Usage

1. Configure Wallet:

```
echo 'PRIVATE_KEY=your_private_key' >> .env
echo 'MNEMONIC=your_mnemonic' >> .env
```

2. Run:(The first run must add --build)

```
sodu docker compose up --build
```

3. You should now be able to `curl` your Unichain node:

```
curl -d '{"id":1,"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",false]}' \
  -H "Content-Type: application/json" http://localhost:8545
```

4. To stop your node, run:

```
docker compose down
```

#### Persisting Data

By default, the data directory is stored in `${PROJECT_ROOT}/geth-data`. You can override this by modifying the value of
`HOST_DATA_DIR` variable in the [`.env`](./.env) file.
