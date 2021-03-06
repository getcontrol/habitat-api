#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from baselines.agents import simple_agents, ppo_agents
import habitat
import os
import pytest

CFG_TEST = "test/habitat_all_sensors_test.yaml"


def test_ppo_agents():
    config = ppo_agents.get_defaut_config()
    config.MODEL_PATH = ""
    config_env = habitat.get_config(config_file=CFG_TEST)
    config_env.defrost()
    if not os.path.exists(config_env.SIMULATOR.SCENE):
        pytest.skip("Please download Habitat test data to data folder.")

    benchmark = habitat.Benchmark(config_file=CFG_TEST, config_dir="configs")

    for input_type in ["blind", "rgb", "depth", "rgbd"]:
        config_env.defrost()
        config_env.SIMULATOR.AGENT_0.SENSORS = []
        if input_type in ["rgb", "rgbd"]:
            config_env.SIMULATOR.AGENT_0.SENSORS += ["RGB_SENSOR"]
        if input_type in ["depth", "rgbd"]:
            config_env.SIMULATOR.AGENT_0.SENSORS += ["DEPTH_SENSOR"]
        config_env.freeze()
        del benchmark._env
        benchmark._env = habitat.Env(config=config_env)
        config.INPUT_TYPE = input_type

        agent = ppo_agents.PPOAgent(config)
        habitat.logger.info(benchmark.evaluate(agent, num_episodes=10))


def test_simple_agents():
    config_env = habitat.get_config(config_file=CFG_TEST)

    if not os.path.exists(config_env.SIMULATOR.SCENE):
        pytest.skip("Please download Habitat test data to data folder.")

    benchmark = habitat.Benchmark(config_file=CFG_TEST, config_dir="configs")

    for agent_class in [
        simple_agents.ForwardOnlyAgent,
        simple_agents.GoalFollower,
        simple_agents.RandomAgent,
        simple_agents.RandomForwardAgent,
    ]:
        agent = agent_class(config_env)
        habitat.logger.info(agent_class.__name__)
        habitat.logger.info(benchmark.evaluate(agent, num_episodes=100))
