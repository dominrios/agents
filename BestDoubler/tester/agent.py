"""
Agent to double any incoming messages on a set topic, publishes out doubled data to a set topic.
"""
__docformat__ = 'reStructuredText'
import logging
import sys
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.9"

class DoublerAgent(Agent):
    """
    DoublerAgent listens to a topic, doubles the numeric values in messages, and publishes them to a set topic.
    """
    def __init__(self, config_path, **kwargs):
        super().__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)
        
        # Default config settings
        self.default_config = {
            "listener_topic": "devices/fake/denis",
            "publish_topic": "fake/dukeee"
        }
        
        self.vip.config.set_default("meow", self.default_config)
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="meow")

    def configure(self, config_name, action, contents):
        """
        Callback from configuration store on changes.
        """

        bruh = self.vip.config.get("meow")
        _log.info(f"oh em gee before everything ok and this is the contents of bro: {bruh}")

        _log.info(f"Config updated: {action}")
        
        # Update the agent's internal configuration
        config = self.default_config.copy()
        config.update(contents)
        
        self._listener_topic = config.get("listener_topic")
        self._publish_topic = config.get("publish_topic")
        
        _log.info(f"Listener topic set to: {self._listener_topic}")
        _log.info(f"Publish topic set to: {self._publish_topic}")

        dood = self.vip.config.list()
        _log.info(f"dawggg this is what we got {dood}")

        bruh = self.vip.config.get("meow")
        _log.info(f"ok and this is the contents of bro: {bruh}")

        # Unsubscribe and subscribe to the new topic configuration
        try:
            self.vip.pubsub.unsubscribe("pubsub", None, self.on_message_received)
        except KeyError:
            pass  # Only unsubscribe if already subscribed

        self.vip.pubsub.subscribe("pubsub", prefix=self._listener_topic, callback=self.on_message_received)

    def on_message_received(self, peer, sender, bus, topic, headers, message):
        """Call back function to send back the message"""
        _log.debug(f"Received message on topic: {topic} our message is: {message}")
        doubled_message = self._double_message(message=message)
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

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        _log.info("DoublerAgent is shutting down")

def main():
    """Main method called to start the agent."""
    utils.vip_main(DoublerAgent, version=__version__)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass