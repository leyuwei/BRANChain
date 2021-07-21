gnome-terminal --tab -t "ue" -- bash -c "sh ./start_ue.sh;exec bash"
sleep 1
pids=$(pgrep -n geth)
echo "monitor $pids"
gnome-terminal --tab -t "ue_mon" -- bash -c "resmon -p -o ue_mon.csv --ps-pids $pids;exec bash"

gnome-terminal --tab -t "ap" -- bash -c "sh ./start_ap.sh;exec bash"
sleep 1
pids=$(pgrep -n geth)
echo "monitor $pids"
gnome-terminal --tab -t "ap_mon" -- bash -c "resmon -p -o ap_mon.csv --ps-pids $pids;exec bash"

gnome-terminal --tab -t "miner" -- bash -c "sh ./start_miner.sh;exec bash"
sleep 1
pids=$(pgrep -n geth)
echo "monitor $pids"
gnome-terminal --tab -t "miner_mon" -- bash -c "resmon -p -o miner_mon.csv --ps-pids $pids;exec bash"

sleep 3
gnome-terminal --tab -t "build_env" -- bash -c "sh ./build_env.sh;exec bash"

sleep 10
echo "start ap_controller"
gnome-terminal --tab -t "ap_controller" -- bash -c "python3 ap_server.py;exec bash"
sleep 3
echo "start ue_controller"
gnome-terminal --tab -t "ue_controller" -- bash -c "python3 ue_client.py;exec bash"
