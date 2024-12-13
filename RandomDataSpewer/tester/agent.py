"""
Agent to generate and publish random data periodically.
"""

__docformat__ = 'reStructuredText'
import logging
import sys
import random
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC
from volttron.platform.scheduling import periodic

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"

def tester(config_path, **kwargs):
    """Parses the Agent configuration and returns an instance of the agent."""
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}
    if not config:
        _log.info("Using Agent defaults for starting configuration.")
    setting1 = int(config.get('setting1', 1))
    setting2 = config.get('setting2', "some/random/topic")
    return RandomDataSpewer(setting1, setting2, **kwargs)

class RandomDataSpewer(Agent):
    """
    Spews random data onto the message bus at a set interval.
    """
    def __init__(self, setting1=1, setting2="some/random/topic", **kwargs):
        super(RandomDataSpewer, self).__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)
        self.setting1 = setting1
        self.setting2 = setting2
        self._publish_topic = "devices/fake/simpleFloat"
        self._subscribe_topic = "fake/doubled"
        
        self.default_config = {"setting1": setting1, "setting2": setting2}
        
        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")
    
    def configure(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)
        _log.debug("Configuring Agent")
        try:
            setting1 = int(config["setting1"])
            setting2 = str(config["setting2"])
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))
            return
        self.setting1 = setting1
        self.setting2 = setting2
        self._create_subscriptions(self.setting2)
    
    def _create_subscriptions(self, topic):
        self.vip.pubsub.unsubscribe('pubsub', prefix=topic, callback=self._handle_publish)
        self.vip.pubsub.subscribe('pubsub', prefix=self._subscribe_topic, callback=self._handle_publish)
    
    def _handle_publish(self, peer, sender, bus, topic, headers, message):
        _log.info(f"Received doubled data over topic: {topic}, data: {message}")
    
    @Core.schedule(periodic(13))  # Adjust interval as needed
    def _spew_data(self):
        rand_int = random.randint(1, 100)
        data = {"awesome_int": rand_int}
        self.vip.pubsub.publish('pubsub', topic=self._publish_topic, message=data)
        _log.info(f"Published random data: {data} topic {self._publish_topic}")
    
    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        _log.info("Agent started and publishing random data.")
    
    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        _log.info("Agent stopping.")
    
    @RPC.export
    def rpc_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
        return self.setting1 + arg1 - arg2

def main():
    """Main method called to start the agent."""
    utils.vip_main(tester, version=__version__)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass