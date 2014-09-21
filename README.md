##Dependence##
+ numpy
+ scipy
+ sklearn
+ pygame

##Introduction##
This is a wlan positioning solution framework.
It is proposed on the basis of machine learning and therefore composed of two phases: 
+ offline phase
  1. process raw data
  2. train model
+ online phase
  1. launch positioning server
  2. predict user's position
This frameword is implemented as client-server mode.

##Usage##
1. data
first of all, make a new directory and put your offline-phase data into 'raw_data/[your_dataset]'
put recieved signal strength(RSS) files into 'raw_data/[your_dataset]/rss'
put map infomations into 'raw_data/[your_dataset]/map'
and put test data into 'raw_data/[your_dataset]/test'

2. run framework
    ```bash
    ./go.py -d [dataset] -a [alg]
    ./go.py -d [dataset] -a [alg] env
    ./go.py -d [dataset] -a [alg] offline
    ./go.py -d [dataset] -a [alg] online
    ```
    + options:
      + -d: specify your dataset in raw_data
      + -a: specify your machine learning algorithm in alg
    + arguments:
      + env: build an environment for further operation
      + offline: execute offline operation, should execute env first
      + online: execute online operation, should execute env and offline first
      + test: should be used seperately
      + nothing specified: will execute env, offline and online sequentially

3. run PC client
    ```bash
    ./pc_client.py
    ```

4. run phone client
   use app in phone_client

5. useful tools
   + rss collector
     in phone_collector directory
   + map information collector
     in offline_tool directory

##BUG REPORT##
+ zchgeek@gmail.com
+ wchgeek@gmail.com
