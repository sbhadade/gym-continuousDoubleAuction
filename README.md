This is **WIP**.

# What's in this repository?
A custom MARL (multi-agent reinforcement learning) environment where multiple
agents trade against one another in a CDA (continuous double auction).

The environment doesn't use any external data. Data is generated by self play
of the agents themselves through their interaction with the limit order book.

At each time step, the environment emits the top k rows of the aggregated
order book as observations to the agents.

# Example:
An example of using RLlib to pit 1 PPO (Proximal Policy Optimization) agent
against 3 random agents using this CDA environment is available in:
```
CDA_env_disc_RLlib.py
```

To run:
```
$ cd gym-continuousDoubleAuction/gym_continuousDoubleAuction

$ python CDA_env_disc_RLlib.py
```

Sample training output results:
```
.
.
.
Result for PPO_continuousDoubleAuction-v0_0:
  custom_metrics: {}
  date: 2019-09-30_21-16-20
  done: true
  episode_len_mean: 1001.0
  episode_reward_max: 0.0
  episode_reward_mean: 0.0
  episode_reward_min: 0.0
  episodes_this_iter: 4
  episodes_total: 38
  experiment_id: 56cbdad4389343eca5cfd49eadeb3554
  hostname: Duality0.local
  info:
    grad_time_ms: 15007.219
    learner:
      policy_0:
        cur_kl_coeff: 0.0003906250058207661
        cur_lr: 4.999999873689376e-05
        entropy: 10.819798469543457
        entropy_coeff: 0.0
        kl: 8.689265087014064e-06
        model: {}
        policy_loss: 153.9163055419922
        total_loss: 843138688.0
        vf_explained_var: 0.0
        vf_loss: 843138496.0
    num_steps_sampled: 40000
    num_steps_trained: 40000
    opt_peak_throughput: 266.538
    opt_samples: 4000.0
    sample_peak_throughput: 80.462
    sample_time_ms: 49713.208
    update_time_ms: 176.14
  iterations_since_restore: 10
  node_ip: 192.168.1.12
  num_healthy_workers: 2
  off_policy_estimator: {}
  pid: 10220
  policy_reward_mean:
    policy_0: 12414.421052631578
    policy_1: -301.39473684210526
    policy_2: -952.1578947368421
    policy_3: -11160.868421052632
  sampler_perf:
    mean_env_wait_ms: 18.1753569144153
    mean_inference_ms: 4.126144958830859
    mean_processing_ms: 1.5262831265657335
  time_since_restore: 649.1416146755219
  time_this_iter_s: 61.54709506034851
  time_total_s: 649.1416146755219
  timestamp: 1569849380
  timesteps_since_restore: 40000
  timesteps_this_iter: 4000
  timesteps_total: 40000
  training_iteration: 10
  trial_id: ea67f638

2019-09-30 21:16:20,507	WARNING util.py:145 -- The `process_trial` operation took 0.4397752285003662 seconds to complete, which may be a performance bottleneck.
2019-09-30 21:16:21,407	WARNING util.py:145 -- The `experiment_checkpoint` operation took 0.899777889251709 seconds to complete, which may be a performance bottleneck.
== Status ==
Using FIFO scheduling algorithm.
Resources requested: 0/4 CPUs, 0/0 GPUs
Memory usage on this node: 3.3/4.3 GB
Result logdir: /Users/hadron0/ray_results/PPO
Number of trials: 1 ({'TERMINATED': 1})
TERMINATED trials:
 - PPO_continuousDoubleAuction-v0_0:	TERMINATED, [3 CPUs, 0 GPUs], [pid=10220], 649 s, 10 iter, 40000 ts, 0 rew

== Status ==
Using FIFO scheduling algorithm.
Resources requested: 0/4 CPUs, 0/0 GPUs
Memory usage on this node: 3.3/4.3 GB
Result logdir: /Users/hadron0/ray_results/PPO
Number of trials: 1 ({'TERMINATED': 1})
TERMINATED trials:
 - PPO_continuousDoubleAuction-v0_0:	TERMINATED, [3 CPUs, 0 GPUs], [pid=10220], 649 s, 10 iter, 40000 ts, 0 rew
```

Running the following tensorboard command & navigate to ```localhost:6006``` in
your browser to access the tensorboard graphs:
```
$ tensorboard --logdir ~/ray_results
```

The figure below from Tensorboard shows the agents' performance:

![](https://github.com/ChuaCheowHuan/gym-continuousDoubleAuction/blob/master/pic/agent0and1.png)
![](https://github.com/ChuaCheowHuan/gym-continuousDoubleAuction/blob/master/pic/agent2and3.png)

PPO agent is using policy 0 while policies 1 to 3 are used by the random agents.

# Dependencies:
Please see `requirements.txt` in this repository.

# Installation:
The environment is installable via pip.
```
$ cd gym-continuousDoubleAuction

$ pip install -e .
```

# TODO:
1) custom RLlib workflow to include custom RND + PPO policies.
2) parametric or hybrid action space
3) more robust tests
3) better documentation

# Acknowledgements:
The orderbook matching engine is adapted from
https://github.com/dyn4mik3/OrderBook

# Contributing:
Please see [CONTRIBUTING.md](https://github.com/ChuaCheowHuan/gym-continuousDoubleAuction/blob/master/CONTRIBUTING.md).

# Disclaimer:
This repository is only meant for research purposes & is **never** meant to be
used in any form of trading. Past performance is no guarantee of future results.
If you suffer losses from using this repository, you are the sole person
responsible for the losses. The author will **NOT** be held responsible in any
way.
