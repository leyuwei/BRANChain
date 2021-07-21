# ![image-20210616131138969](readme.assets/image-20210616131138969.png)BRANChain Network Guidelines

**`Version`** 20210621 V2.0

**`Author`** Yuwei Le



## How to prepare this program for testing

1. **If you are using Windows**, you can run `install_env_windows.bat` in the root directory to let the script set up the environment for you automatically. **Please remember to turn off all the proxies on your system before running this script.**
2. **If you are using Linux (or other Linux-based systems)**, you can run `pip install -r requirements.txt` from the root directory.

In order to let the program adapt to as many systems/platforms as we can, we list some common errors and their solutions down below.

1. **miniupnpc cannot be installed using pip command?**

   miniupnpc is a special package for node communication. Its compatibility with Python is relatively poor and developers have to compile their own binaries from the source code provided by miniupnpc official. So far, we have collected some of the compiled binaries in the `tools\miniupnpc` folder, and you can install one of them based on your environment (by running `pip install XXX.whl` command).

   In case that there is no available binary for your environment, please refer to https://pypi.chia.net/simple/miniupnpc/  

2. **Python cannot find Crypto package on Windows?**

   After installing the requirements.txt, you may find that the Python still cannot recognize Crypto package. In this case:

   Goto `Python37\Lib\site-packages` folder (you can just search `site-packages` folder in your explorer) and rename the `crypto` directory to `Crypto`.



## How to test and reproduce results in the paper

The simplest way is to run `sim_main_network_simplest.py`. It creates three essential nodes as the minimum requirement of B-RAN network.
In our paper, except for the resource consumption parts, we just use this script. For analyzing the power consumption and flame graphs, you can run `sim_main_network_cmd.py` for starting a random node with custom settings.
However, if you want to replicate the results in our paper, please see `tester` folder and choose between `resmon_perf_linux.sh` and `resmon_mprof_linux.sh`. Notice that you must run the above scripts in a Linux-based system and make sure you have installed all the required packages.

Numerical results can also be tested without the network. An earlier version that we developed does not include designs of network nodes and pluggable consensus. It lets B-RAN run based on pre-calculated events and a bunch of given parameters. You can enable this old version by starting from `sim_main_parallel_use_rho.py`  and `sim_main_spt.py`.



## Updates

- increase the program performance by 10X and now you can get your simulation results within seconds!
- increase the CPU and memory utilization when you run this program in parallel mode.
- fix a critical bug that is caused by a flawed integer randomization design, which may let the program hang forever.
- fix a bug that latency values collected from sim_main scripts do not exclude the service phase, which could be unexpectedly large.
* fix a bug that may cause ZeroDivisionException when using sim_main_network_cmd.py alone.
- add resmon_perf_linux tester that should be used with FlameGraph in the tool folder
- sim_main_network_cmd.py can now support is_mining_for_real, blocktime, and prob_error settings