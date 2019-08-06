#import tensorflow as tf

import ray
from ray.rllib.env.multi_agent_env import MultiAgentEnv

from gym import spaces

from .exchg_helper import Exchg_Helper
#from .orderbook import OrderBook
from .orderbook.orderbook import OrderBook
from .trader import Trader

# The exchange environment
class Exchg(Exchg_Helper, MultiAgentEnv):
    def __init__(self, num_of_agents=2, init_cash=0, tick_size=1, tape_display_length=10, max_step=100):
        super(Exchg, self).__init__(init_cash, tick_size, tape_display_length)

        self.next_states = {}
        self.rewards = {}
        self.dones = {}
        self.done_set = set()
        self.infos = {}

        # step when actions by all traders are executed, not tick time
        # within a step, multiple trades(ticks) could happened
        self.t_step = 0
        self.max_step = max_step

        # list of agents or traders
        self.agents = [Trader(ID, init_cash) for ID in range(0, num_of_agents)]

        # observation space per agent:
        # array([[ 1.,  0., -1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
        #        [-1., -4., -4.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
        #        [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
        #        [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
        inf = float('inf')
        neg_inf = float('-inf')
        obs_row = 4
        obs_col = 10
        self.observation_space = spaces.Box(low=neg_inf, high=inf, shape=(obs_row,obs_col))

        # ********** NEED TO PREPROCESS ACTION FROM NN BEFORE EXECUTION **********
        # NEED TO DECODE type_side
        # NEED TO ADD trader.ID before randomizing execution sequence
        # order per agent: {'ID': 0, 'type': 'market', 'side': 'bid', 'size': 1, 'price': 8}
        # action space per agent: {'type_side': 0-4, 'size': 1-inf, 'price': tick_size-inf}
        """
        self.action_space = spaces.Tuple((spaces.Discrete(5),
                                          spaces.Box(low=1.0, high=999.0, shape=(1,)),
                                          spaces.Box(low=1.0, high=999.0, shape=(1,)),
                                        ))
        """

        self.action_space = spaces.Tuple((spaces.Box(low=0.0, high=4.0, shape=(1,)),
                                          spaces.Box(low=1.0, high=999.0, shape=(1,)),
                                          spaces.Box(low=1.0, high=999.0, shape=(1,)),
                                        ))

        #self.action_space = spaces.MultiDiscrete([5, 100, 10]) # type_side, size, price

    # reset
    def reset(self):

        self.render()

        self.LOB = OrderBook(1, self.tape_display_length) # new limit order book
        #self.LOB = OrderBook(0.25, self.tape_display_length) # new limit order book
        self.agg_LOB = {}
        self.agg_LOB_aft = {}

        self.next_states = {}
        self.rewards = {}
        self.dones = {}
        self.done_set = set()
        self.infos = {}

        self.trades = {} # a trade between init_party & counter_party
        self.order_in_book = {} # unfilled orders goes to LOB

        self.t_step = 0

        self.reset_traders_acc()

        return self.reset_traders_agg_LOB()

    # actions is a list of actions from all agents (traders) at t step
    # each action is a list of (ID, type, side, size, price)
    def step(self, actions):

        print('step actions:', actions)
# clip & floor div before passing into LOB
# step actions: {0: array([ 1.1145465,  2.0979862, -1.5236733], dtype=float32), 1: array([-0.5973312 ,  4.129451  , -0.29671174], dtype=float32)}
# (pid=9574) actions: [{'ID': 0, 'type': 'limit', 'side': 'ask', 'size': 2.0979862, 'price': -1.5236733}, {'ID': 1, 'type': 'limit', 'side': 'ask', 'size': 4.129451, 'price': -0.29671174}]
# (pid=9574) shuffle_actions: [{'ID': 1, 'type': 'limit', 'side': 'ask', 'size': 4.129451, 'price': -0.29671174}, {'ID': 0, 'type': 'limit', 'side': 'ask', 'size': 2.0979862, 'price': -1.5236733}]

        self.next_states, self.rewards, self.dones, self.infos = {}, {}, {}, {}
        self.agg_LOB = self.set_agg_LOB() # LOB state at t before processing LOB
        actions = self.set_actions(actions) # format actions from nn output to be acceptable by LOB
        actions = self.rand_exec_seq(actions, 0) # randomized traders execution sequence
        self.do_actions(actions) # Begin processing LOB
        self.mark_to_mkt() # mark to market
        # after processing LOB
        state_input = self.prep_next_state()
        self.next_states, self.rewards, self.dones, self.infos = self.set_step_outputs(state_input)
        self.t_step += 1

        #self.render()

        return self.next_states, self.rewards, self.dones, self.infos

    # render
    def render(self):

        print('\n********** render **********:\n', self.dones)

        print('\nt_step:\n', self.t_step)
        #print('\nLOB:\n', self.LOB)
        #print('\nagg_LOB:\n', self.agg_LOB)
        #print('\nagg_LOB_aft:\n', self.agg_LOB_aft)
        #print('\nnext_states:\n', self.next_states)
        #print('\nrewards:\n', self.rewards)
        print('\ndones:\n', self.dones)
        #print('\ninfos:\n', self.infos)
        self.print_accs()
        print('total_sys_profit:', self.total_sys_profit())
        print('total_sys_nav:', self.total_sys_nav())
        return 0
