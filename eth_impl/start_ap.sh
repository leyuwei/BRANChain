geth --datadir ap --networkid 20201023 init genesis.json 2>>ap.log
cp -rf ap_keystore/keystore ap
echo "AP has been initialized"
geth --datadir ap --metrics --port 30304 --rpc --rpcport 8546 --rpcapi admin,personal,eth,net,web3,miner --networkid 20201023 --allow-insecure-unlock 2>>ap.log &
echo "AP has started. Connected to the same network (20201023)"

