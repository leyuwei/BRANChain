geth --datadir ue --networkid 20201023 init genesis.json 2>>ue.log
cp -rf ue_keystore/keystore ue
echo "UE has been initialized."
geth --datadir ue --metrics --port 30303 --rpc --rpcport 8545 --rpcapi admin,personal,eth,net,web3,miner --networkid 20201023 --allow-insecure-unlock 2>>ue.log &
echo "UE has started."
