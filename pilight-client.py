import settings
import pika
import pika.exceptions
import base64
import traceback
import sys
import time
from pika.exceptions import ConnectionClosed


class PilightClient(object):

    def __init__(self):
        self.num_lights = 0

    def clear_lights(self, spidev):
        if not spidev:
            return

        raw_data = bytearray(self.num_lights * 3)
        for i in range(self.num_lights * 3):
            raw_data[i] = 0x00
        spidev.write(raw_data)
        spidev.flush()

    def run_client(self, spidev):
        print 'PiLight Client running...'

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
            self.num_lights = len(raw_data) / 3
            if not settings.NOOP:
                spidev.write(raw_data)
                spidev.flush()


client = PilightClient()
while True:
    spidev = None
    try:
        # Attempt to open the SPI device
        if not settings.NOOP:
            try:
                spidev = file(settings.SPI_DEV_NAME, 'wb')
            except:
                # Ugly catch-all...
                print 'Exception opening SPI device!'
                traceback.print_exc(file=sys.stdout)
                exit(-1)

        # Run the actual driver loop
        client.run_client(spidev)
        # Sometimes we exit without an exception - always wait before retrying
        time.sleep(30)
    except KeyboardInterrupt:
        # The user has interrupted execution - close our resources
        if spidev:
            client.clear_lights(spidev)
            spidev.close()
            spidev = None
        exit(0)
    except:
        # Eat any other exceptions - retry connecting in 30s
        print 'Connection lost - retrying in 30s'
        time.sleep(30)
    finally:
        if spidev:
            client.clear_lights(spidev)
            spidev.close()
            spidev = None
