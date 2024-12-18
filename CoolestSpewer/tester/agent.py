"""
Agent to generate and publish random data periodically.
"""
__docformat__ = 'reStructuredText'
import logging
import sys
import random
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.scheduling import periodic


_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "1.2"

class RandomDataSpewer(Agent):
    def __init__(self, config_path, **kwargs):
        super().__init__(**kwargs)
        self.default_config = {
            "publish_topic": "devices/fake/simpleFloat",
            "subscribe_topic": "faked/doubled",
            "interval": 7
        }
        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")

    def configure(self, config_name, action, contents):
        _log.debug("Configuring Agent")
        config = self.default_config.copy()
        config.update(contents)
        self._publish_topic = config.get("publish_topic")
        self._subscribe_topic = config.get("subscribe_topic")
        self._interval = config.get("interval")
        self._create_subscriptions()
        self.core.periodic(self._interval, self._spew_data)


    def _create_subscriptions(self):
        self.vip.pubsub.unsubscribe('pubsub', prefix=self._subscribe_topic, callback=self._handle_publish)
        self.vip.pubsub.subscribe('pubsub', prefix=self._subscribe_topic, callback=self._handle_publish)

    def _handle_publish(self, peer, sender, bus, topic, headers, message):
        _log.info(f"Received doubled data over topic: {topic}, data: {message}")

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        _log.info("Agent started and scheduling periodic task.")
        # Schedule the periodic task here

    def _spew_data(self):
        rand_int = random.randint(1, 100)
        data = {"awesome_int": rand_int}
        self.vip.pubsub.publish('pubsub', topic=self._publish_topic, message=data)
        _log.info(f"Published random data: {data} topic {self._publish_topic}")

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        _log.info("Agent stopping.")

def main():
    utils.vip_main(RandomDataSpewer, version=__version__)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass