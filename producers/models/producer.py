"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroConsumer, AvroProducer, CachedSchemaRegistryClient



logger = logging.getLogger(__name__)


class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        #
        #
        # TODO: Configure the broker properties
        self.broker_properties = {
            "BROKER_URL": "PLAINTEXT://localhost:9092",
            "SCHEMA_REGISTRY_URL": "http://localhost:8081",
            "group.id": f"{self.topic_name}",

        }


        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # TODO: Configure the AvroProducer
        self.producer = AvroProducer(
            {'bootstrap.servers': self.broker_properties["BROKER_URL"]},
            schema_registry = CachedSchemaRegistryClient(
                {"url": self.broker_properties["SCHEMA_REGISTRY_URL"]},
            )
        )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        # TODO: Write code that creates the topic for this producer if it does not already exist on
        # the Kafka Broker.
        # See: https://docs.confluent.io/current/clients/confluent-kafka-python/#confluent_kafka.admin.AdminClient
        client = AdminClient({"bootstrap.servers": self.broker_properties['BROKER_URL']})

        logger.info("topic created")

        # Create a NewTopic object
        # See: https://docs.confluent.io/current/clients/confluent-kafka-python/#confluent_kafka.admin.NewTopic

        topic = NewTopic(self.topic_name,
                          num_partitions=self.num_partitions,
                          replication_factor = self.num_replicas)

        # Using 'client', create the topic
        # See: https://docs.confluent.io/current/clients/confluent-kafka-python/#confluent_kafka.admin.AdminClient.create_topics
        futures = client.create_topics([topic])

        for topic, future in futures.items():
            try:
                future.result()
                print(f"topic created {topic}")
            except Exception as e:
                msg = f"failed to create topic: {e}"
                logger.fatal(msg)
                print(msg)
                raise

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        self.producer.flush()
        logger.info("producer close successfully")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
