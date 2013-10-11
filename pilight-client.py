import settings
import pika
import pika.exceptions
import base64
import traceback
import sys


class PilightClient(object):

    def run_client(self, spidev):
        # Prepare the pika connection
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=settings.PILIGHT_HOST, port=settings.PILIGHT_PORT)
            )
        except pika.exceptions.AMQPConnectionError:
            print 'Error connecting to RabbitMQ server - please check settings'
            return
        channel = connection.channel()
        channel.queue_declare(
            queue=settings.PILIGHT_QUEUE_NAME,
            auto_delete=False,
            durable=True
        )

        # Purge any existing data
        channel.queue_purge(settings.PILIGHT_QUEUE_NAME)

        # Loop until interrupted
        for method, properties, body in channel.consume(settings.PILIGHT_QUEUE_NAME):
            channel.basic_ack(method.delivery_tag)
            raw_data = bytearray(base64.b64decode(body))
            if not settings.NOOP:
                spidev.write(raw_data)
                spidev.flush()


# Attempt to open the SPI device
if settings.NOOP:
    spidev = None
else:
    try:
        spidev = file(settings.SPI_DEV_NAME, 'wb')
    except:
        # Ugly catch-all...
        print 'Exception opening SPI device!'
        traceback.print_exc(file=sys.stdout)
        exit(-1)

client = PilightClient()
client.run_client(spidev)
