This is **WIP**.

# What's in this repository?
A custom MARL (multi-agent reinforcement learning) environment where multiple
agents trade against one another in a CDA (continuous double auction).

The environment doesn't use any external data. Data is generated by the agents
themselves (self play) through their interaction with the limit order book.

# How can you run this?
An example of using RLlib to pit 1 PPO agent against 3 random agents using this
CDA environment is available in CDA_env_disc_RLlib.py

To run:
```
python CDA_env_disc_RLlib.py
```

The figure below from Tensorboard shows the agents' performance:

![](https://github.com/ChuaCheowHuan/MARL_env/blob/master/pic/agent0and1.png)
![](https://github.com/ChuaCheowHuan/MARL_env/blob/master/pic/agent2and3.png)

PPO agent is using policy 0 while policies 1 to 3 are used by the random agents.

# Dependencies:
1) Tensorflow
2) OpenAI's Gym
3) Ray & RLlib

# Installation:
The environment is installable via pip.
```
cd gym-continuousDoubleAuction
```
```
pip install -e .
```

# TODO:
1) custom RLlib workflow to include custom RND + PPO policies.
2) parametric or hybrid action space
3) more documentation

# Acknowledgements:
The orderbook matching engine is adapted from
https://github.com/dyn4mik3/OrderBook

# Disclaimer:
This repository is only meant for research purposes & is **never** meant to be
used in any form of trading. Past performance is no guarantee of future results.
If you suffer losses from using this repository, you are the sole person
responsible for the losses. The author will **NOT** be held responsible in any
way.
