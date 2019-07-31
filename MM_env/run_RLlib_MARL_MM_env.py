# https://github.com/ray-project/ray/blob/master/python/ray/rllib/examples/multiagent_cartpole.py
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
"""Simple example of setting up a multi-agent policy mapping.
Control the number of agents and policies via --num-agents and --num-policies.
This works with hundreds of agents and policies, but note that initializing
many TF policies will take some time.
Also, TF evals might slow down with large numbers of policies. To debug TF
execution, set the TF_TIMELINE_DIR environment variable.
"""
import argparse
import gym
import random
import numpy as np

import ray
from ray import tune
from ray.rllib.models import Model, ModelCatalog
from ray.rllib.tests.test_multi_agent_env import MultiCartpole
from ray.tune.registry import register_env
from ray.rllib.utils import try_import_tf




import unittest

from ray.rllib.agents.pg import PGTrainer
from ray.rllib.agents.pg.pg_policy import PGTFPolicy
from ray.rllib.agents.dqn.dqn_policy import DQNTFPolicy
from ray.rllib.optimizers import (SyncSamplesOptimizer, SyncReplayOptimizer,
                                  AsyncGradientsOptimizer)
from ray.rllib.tests.test_rollout_worker import (MockEnv, MockEnv2, MockPolicy)
from ray.rllib.evaluation.rollout_worker import RolloutWorker
from ray.rllib.policy.policy import Policy
from ray.rllib.evaluation.metrics import collect_metrics
from ray.rllib.evaluation.worker_set import WorkerSet
from ray.rllib.env.base_env import _MultiAgentEnvToBaseEnv
from ray.rllib.env.multi_agent_env import MultiAgentEnv



import sys
if "../" not in sys.path:
    sys.path.append("../")
#from exchg.x.y import z
from exchg.exchg import Exchg

tf = try_import_tf()

parser = argparse.ArgumentParser()

parser.add_argument("--num-agents", type=int, default=4)
#parser.add_argument("--num-policies", type=int, default=2)
parser.add_argument("--num-policies", type=int, default=1)
parser.add_argument("--num-iters", type=int, default=20)
parser.add_argument("--simple", action="store_true")

class CustomModel1(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        # Example of (optional) weight sharing between two different policies.
        # Here, we share the variables defined in the 'shared' variable scope
        # by entering it explicitly with tf.AUTO_REUSE. This creates the
        # variables for the 'fc1' layer in a global scope called 'shared'
        # outside of the policy's normal variable scope.
        with tf.variable_scope(tf.VariableScope(tf.AUTO_REUSE, "shared"),
                               reuse=tf.AUTO_REUSE,
                               auxiliary_name_scope=False):
            last_layer = tf.layers.dense(input_dict["obs"], 64, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(last_layer, 64, activation=tf.nn.relu, name="fc2")
        #output = tf.layers.dense(last_layer, num_outputs, activation=None, name="fc_out")



        # ********** TESTING **********
        num_outputs = 1
        num_type_side = 5

        prob_weights = tf.layers.dense(last_layer, num_outputs * num_type_side, activation=tf.nn.softmax, name="prob_weights")
        #type_side = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())
        type_side = np.random.choice(range(prob_weights.shape[1]), p=prob_weights)

        mu_size = tf.layers.dense(last_layer, num_outputs, activation=tf.nn.tanh, name="mu_size")
        sigma_size = tf.layers.dense(last_layer, num_outputs, activation=tf.nn.softplus, name="sigma_size")

        mu_price = tf.layers.dense(last_layer, num_outputs, activation=tf.nn.tanh, name="mu_price")
        sigma_price = tf.layers.dense(last_layer, num_outputs, activation=tf.nn.softplus, name="sigma_price")

        norm_dist_size = tf.distributions.Normal(loc=mu_size, scale=sigma_size)
        size = tf.squeeze(norm_dist_size.sample(1), axis=0) # choosing size

        norm_dist_price = tf.distributions.Normal(loc=mu_price, scale=sigma_price)
        price = tf.squeeze(norm_dist_price.sample(1), axis=0) # choosing price

        # ********** output FOR SINGLE AGENT IS TUPLE NOT DICT **********
        #output = {'type_side': type_side,'size': size,'price': price}
        output = (type_side, size, price)

        print('CustomModel1:', output)

        return output, last_layer
        # ********** TESTING **********

        #return output, last_layer



class CustomModel2(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        # Weights shared with CustomModel1
        with tf.variable_scope(tf.VariableScope(tf.AUTO_REUSE, "shared"),
                               reuse=tf.AUTO_REUSE,
                               auxiliary_name_scope=False):
            last_layer = tf.layers.dense(input_dict["obs"], 64, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(last_layer, 64, activation=tf.nn.relu, name="fc2")
        # output are action logits
        output = tf.layers.dense(last_layer, num_outputs, activation=None, name="fc_out")
        return output, last_layer

if __name__ == "__main__":
    num_of_traders = 4
    tape_display_length = 100
    tick_size = 1
    init_cash = 10000
    max_step = 100
    MM_env = Exchg(num_of_traders, init_cash, tick_size, tape_display_length, max_step)
    print('MM_env:', MM_env.print_accs())

    args = parser.parse_args()
    ray.init()

    # Simple environment with `num_agents` independent cartpole entities
    #register_env("multi_cartpole", lambda _: MultiCartpole(args.num_agents))



    # ********** exchg path BUG **********
    register_env("MMenv-v0", lambda _: Exchg(args.num_agents, init_cash, tick_size, tape_display_length, max_step))



    ModelCatalog.register_custom_model("model1", CustomModel1)
    #ModelCatalog.register_custom_model("model2", CustomModel2)
    #single_env = gym.make("CartPole-v0")
    #obs_space = single_env.observation_space
    #act_space = single_env.action_space
    obs_space = MM_env.observation_space
    act_space = MM_env.action_space

    # Each policy can have a different configuration (including custom model)
    def gen_policy(i):
        #config = {"model": {"custom_model": ["model1", "model2"][i % 2],},
        #          "gamma": random.choice([0.95, 0.99]),}
        config = {"model": {"custom_model": "model1"},
                  "gamma": 0.95,}
        return (None, obs_space, act_space, config)

    # Setup PPO with an ensemble of `num_policies` different policies
    policies = {"policy_{}".format(i): gen_policy(i) for i in range(args.num_policies)}
    policy_ids = list(policies.keys())

    tune.run("PPO",
             stop={"training_iteration": args.num_iters},
             #config={"env": "multi_cartpole",
             config={"env": "MMenv-v0",
                     "log_level": "DEBUG",
                     "simple_optimizer": args.simple,
                     "num_sgd_iter": 10,
                     "multiagent": {"policies": policies,
                                    "policy_mapping_fn": tune.function(lambda agent_id: random.choice(policy_ids)),
                                   },
                    },
            )