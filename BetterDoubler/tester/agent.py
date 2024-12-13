"""
Agent to double any incoming messages on a set topic, publishes out doubled data to a set topic.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, RPC

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.9"
DEFAULT_TOPIC_LISTENER = "devices/fake/simpleFloat"

class DoublerAgent(Agent):
    """
    DoublerAgent listens to a topic, doubles the numeric values in messages, and publishes them to a set topic.
    """
    def __init__(self, config_path, **kwargs):
        super().__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)
        self.config = utils.load_config(config_path)
        self._listener_topic = self.config.get("listener_topic", DEFAULT_TOPIC_LISTENER)
        self._publish_topic = self.config.get("publish_topic", "fake/doubled")

    def on_message_received(self, peer, sender, bus, topic, headers, message):
        """Call back function to send back the message"""
        _log.debug(f"Received message on topic: {topic} our message is: {message}")
        doubled_message = str(self._double_message(message=message))
        self.vip.pubsub.publish('pubsub', topic=self._publish_topic, message=doubled_message)
        _log.debug(f"Publishing data: {doubled_message} to topic: {self._publish_topic}")

    def _double_message(self, message) -> dict:
        try:
            formatted_message: dict = eval(message) if isinstance(message, str) else message
            doubled_message = {key: (value * 2 if isinstance(value, (int, float)) else value)
                            for key, value in formatted_message.items()}
            return doubled_message
        except Exception as e:
            _log.error("Failed to double message values due to error: %s", e)
            return message


    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        After the agent has successfully connected, set up subscriptions.
        """
        self.vip.pubsub.subscribe('pubsub',
                                prefix=self._listener_topic,
                                callback=self.on_message_received)
        _log.info(f"DoublerAgent subscribed to {self._listener_topic}")

        # Example publish to pubsub (for illustrative purposes)
        # self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        _log.info("DoublerAgent is shutting down")
        pass

    @RPC.export
    def rpc_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
        """
        RPC method

        May be called from another agent via self.core.rpc.call
        """
        return arg1 - arg2


def main():
    """Main method called to start the agent."""
    utils.vip_main(DoublerAgent, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
