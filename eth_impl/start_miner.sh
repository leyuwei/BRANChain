geth --datadir miner --networkid 20201023 init genesis.json 2>>miner.log
cp -rf miner_keystore/keystore miner
echo "MINER has been initialized"
geth --datadir miner --metrics --port 30305 --rpc --rpcport 8547 --rpcapi admin,personal,eth,net,web3,miner --networkid 20201023 --allow-insecure-unlock 2>>miner.log &
echo "MINER has started. Connected to the same network (20201023)"
