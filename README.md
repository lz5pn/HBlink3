# HBlink3

In this repository have all needed to build working HBlink3 server. It is based on HBlink3 created by N4IRS and include Parrot server. Also here is HBmonitor created by SP2ONG. THis is complete DMR server with WEB based monitor.

It allow communication from DMR radio via Pi-Star via HBlink to another Pi-Star and DMR radio connected to it.

It allow communication from DMR radio via Pi-Star via HBlink to BrandMeister server as peer and DMR radios connected to talk groups in BrandMeister server.

It allow communication from DMR radio via Pi-Star via HBlink to IPSC2 server as peer and DMR radios connected to talk groups in IPSC2 server.

It allow communication from DMR radio via Pi-Star via HBlink to XLX as peer and DMR or D-Star radios connected to XLX.

It allow communication from DMR radio via Pi-Star via HBlink to HBlink as peer and DMR radios connected to talk groups in HBlink.

HBlink server also allow control on traffic. It is possible to setup Talk Group for turn on or off one TG, several TG or all TG. This software provide very good control on DMR traffic, incoming and outgoing to other servers like BrandMeister, IPSC2, XLX and HBlink.

Many thanks to N0MJS creator, N4IRS and SP2ONG for this such nice software.

Originaly this software was created as software for connection between IPSC2 and BrandMeister. Be careful when you use it and create your communication channels. 

This software is very good for small networks of few hotspots or repeater or mix of them. It work very well on Raspberry Pi3 with Raspbian Buster, or on Desktop machine with Linux (tested on Linux Mint)

I do not provide support for this software. If future updates in operating systems make it not working or not possible to be installed, sorry but I'm not going to fix such problems. Use this software on your own risk. If you cause troubles by inapropriate settings or ussage of this software I do not take any responsibility. Everyone who use this software, is responsible for any problems caused in his or other networks.

Follow the next commands in terminal to install HBlink and HBmonitor on raspbian buster or Linux Mint:

apt update

apt upgrade

apt dist-upgrade

apt autoremove

apt autoclean

#install hblink

apt install git

apt install python3-distutils

cd /opt/

wget https://bootstrap.pypa.io/get-pip.py

python3 get-pip.py

apt install python3-twisted

apt install python3-bitarray

apt install python3-dev

git clone https://github.com/lz5pn/HBlink3

mv /opt/HBlink3/ /opt/backup/

mv /opt/backup/HBlink3/ /opt/

mv /opt/backup/HBmonitor/ /opt/

mv /opt/backup/dmr_utils3/ /opt/

rm -r /opt/backup/

cd /opt/dmr_utils3

chmod +x install.sh

./install.sh

/usr/bin/python3 -m pip install --upgrade pip

pip install --upgrade dmr_utils3

cd /opt/HBlink3

cp hblink-SAMPLE.cfg hblink.cfg

cp rules-SAMPLE.py rules.py

Autostart HBLink:

nano /lib/systemd/system/hblink.service

Copy and paste the next:

------------------------------------------------------------------------------------------------------------------------
[Unit]

Description=Start HBlink

After=multi-user.target

[Service]

ExecStart=/usr/bin/python3 /opt/HBlink3/bridge.py

[Install]

WantedBy=multi-user.target

------------------------------------------------------------------------------------------------------------------------

systemctl daemon-reload

systemctl enable hblink


Install Parrot for Echotest:

chmod +x playback.py


Create directory for registration files, if /var/log/hblink is not created.

mkdir /var/log/hblink

To start Parrot service must use file /lib/systemd/system/parrot.service 

nano /lib/systemd/system/parrot.service

Copy and paste the next:

------------------------------------------------------------------------------------------------------------------------
[Unit]

Description=HB bridge all Service

After=network-online.target syslog.target

Wants=network-online.target

[Service]

StandardOutput=null

WorkingDirectory=/opt/HBlink3

RestartSec=3

ExecStart=/usr/bin/python3 /opt/HBlink3/playback.py -c /opt/HBlink3/playback.cfg

Restart=on-abort

[Install]

WantedBy=multi-user.target

------------------------------------------------------------------------------------------------------------------------

Start Parrot service:

systemctl enable parrot.service

systemctl start parrot.service

systemctl status parrot.service

nano /opt/HBlink3/rules.py

Test configuration:

python3 /opt/HBlink3/bridge.py

systemctl start hblink

systemctl status hblink

Install web monitor for HBLink.

cd /opt/HBmonitor

chmod +x install.sh

./install.sh

cp config_SAMPLE.py config.py

nano /opt/HBmonitor/config.py

Start monitor as system service:

cp utils/hbmon.service /lib/systemd/system/

systemctl enable hbmon

systemctl start hbmon

systemctl status hbmon

forward TCP ports 8080 and 9000 in router firewall


My HBlink servers: http://kario88.dynamic-dns.net:8184/ and http://lz5pn.freeddns.com:8184/


73 de LZ5PN
