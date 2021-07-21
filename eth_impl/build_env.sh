
ue_enode_addr=$(geth attach "rpc:http://localhost:8545" << EOF | grep "Data: " | sed "s/Data: //")
var addr = admin.nodeInfo.enode;
console.log("Data: " + addr);
exit;
EOF
echo "UE enode address: ${ue_enode_addr}"

ap_enode_addr=$(geth attach "rpc:http://localhost:8546" << EOF | grep "Data: " | sed "s/Data: //")
var addr = admin.nodeInfo.enode;
console.log("Data: " + addr);
exit;
EOF
echo "AP enode address: ${ap_enode_addr}"

miner_enode_addr=$(geth attach "rpc:http://localhost:8547" << EOF | grep "Data: " | sed "s/Data: //")
var addr = admin.nodeInfo.enode;
console.log("Data: " + addr);
exit;
EOF
echo "MINER enode address: ${miner_enode_addr}"





sleep 1
# Networking
echo "Networking ..."

conn_status_13=$(geth attach "rpc:http://localhost:8545" << EOF | grep "Data: " | sed "s/Data: //")
var connstatus = admin.addPeer("$miner_enode_addr");
console.log("Data: " + connstatus);
exit;
EOF
echo "UE has connected to MINER with status=${conn_status_13}"

conn_status_21=$(geth attach "rpc:http://localhost:8546" << EOF | grep "Data: " | sed "s/Data: //")
var connstatus = admin.addPeer("$ue_enode_addr");
console.log("Data: " + connstatus);
exit;
EOF
echo "AP has connected to UE with status=${conn_status_21}"

conn_status_32=$(geth attach "rpc:http://localhost:8547" << EOF | grep "Data: " | sed "s/Data: //")
var connstatus = admin.addPeer("$ap_enode_addr");
console.log("Data: " + connstatus);
exit;
EOF
echo "MINER has connected to AP with status=${conn_status_32}"


peerInfo_1=$(geth attach "rpc:http://localhost:8545" << EOF | grep "Data: " | sed "s/Data: //")
var peerinfo = net.peerCount;
console.log("Data: " + peerinfo);
exit;
EOF
echo "Checking connection on UE: ${peerInfo_1} < should see 2"

peerInfo_2=$(geth attach "rpc:http://localhost:8546" << EOF | grep "Data: " | sed "s/Data: //")
var peerinfo = net.peerCount;
console.log("Data: " + peerinfo);
exit;
EOF
echo "Checking connection on AP: ${peerInfo_2} < should see 2"

peerInfo_3=$(geth attach "rpc:http://localhost:8547" << EOF | grep "Data: " | sed "s/Data: //")
var peerinfo = net.peerCount;
console.log("Data: " + peerinfo);
exit;
EOF
echo "Checking connection on MINER: ${peerInfo_3} < should see 2"

miner_account=$(geth attach "rpc:http://localhost:8547" << EOF | grep "Data: " | sed "s/Data: //")
personal.newAccount("1234");
personal.unlockAccount(eth.accounts[0], "1234", 10000)
var miner_account = eth.accounts[0];
console.log("Data: " + miner_account);
exit;
EOF
echo "MINER has created a new account: ${miner_account} with pwd=1234"

sleep 1
# Start mining
echo "Start mining on MINER. Data should be sychronized to UE and AP shortly after DAG gets 100% initialized"
miner_stat=$(geth attach "rpc:http://localhost:8547" << EOF | grep "Data: " | sed "s/Data: //")
miner.setEtherbase(eth.coinbase);
var stat = miner.start(1);
admin.sleepBlocks(1);
console.log("Data: " + stat);
exit;
EOF
echo "miner stat: ${miner_stat} < should see null"

