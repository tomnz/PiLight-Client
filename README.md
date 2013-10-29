PiLight Client
==============

Lightweight client designed to run on a Raspberry Pi, poll a RabbitMQ server (potentially running on another device) for color data, and output that color data to a WS2801 LED string.

This application is essentially useless on its own, as it expects to receive color data (it does not produce any of its own). The [PiLight](https://bitbucket.org/tomnz/pilight) project is a suitable supplier of this data.

Installation
------------

Install all prerequisites first:

* [Python](http://www.python.org/download/) - 2.7 recommended
* [RabbitMQ](http://www.rabbitmq.com/download.html) (requires [Erlang](http://www.erlang.org/download.html))
* [pip](https://pypi.python.org/pypi/pip/) strongly recommended to install extra Python dependencies

> Note: These instructions assume you're using a Raspberry Pi with Occidentalis for the most part - omit sudo if your flavor doesn't use it, for example. This is all tested working with a 512MB Raspberry Pi device, and Occidentalis v0.2.

Download the source to a desired location:

    hg clone https://bitbucket.org/tomnz/pilight-client

Install the Python dependencies:

    cd pilight-client
    sudo pip install -r requirements.txt

> Note: If you get an error message about available space on the device, it's likely your /tmp folder is too small. Run `sudo nano /etc/default/tmpfs`, change TMP_SIZE to 200M, then try `pip install -r requirements.txt` again. You may run into this when installing on a Raspberry Pi device.

Copy the settings file and make required changes (particularly set up your RabbitMQ server address):

    cp settings.py.default settings.py

> Note: Be sure to edit your new settings.py file!


Launch PiLight
--------------

Once you've gone through all the installation steps, you're ready to run PiLight Client!

Simply run the following command:

    sudo python pilight-client.py

This will attempt to connect to the target RabbitMQ server and await color data. If you receive a connection error, make sure you've configured the host name correctly, that RabbitMQ is running on the server, and that the RabbitMQ port is opened on your firewall.


Updating
--------

Periodically you may want to update PiLight Client to get the latest features and bug fixes. Just run the following commands from the `pilight-client` directory:

    hg pull
    hg update