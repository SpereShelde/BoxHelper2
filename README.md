# boxHelper2

[中文版](https://github.com/SpereShelde/boxHelper2/blob/master/README-zh.md)

This is a new version of boxHelper based on python3. Unlike the previous version, boxHelper2 is designed to be compatible with a wide range of websites. It relies on RSS to get patterns and torrent info.

## Usage

### Environment
apt install python3
apt install python3-pip
pip3 install virtualenv

### Install

#### Download

`wget -O 'boxHelper2.zip' 'https://github.com/SpereShelde/boxHelper2/archive/master.zip'`

#### Unzip

`unzip boxHelper2.zip`

#### Virtual env

`cd boxHelper2 && mkdir ENV && cd ENV`

`source ./bin/activate`

#### Install requirements

`cd .. && pip3 install -r requirements.txt`

#### Write config

`nano config.ini`

#### Run

`gunicorn -b 0.0.0.0:12020 app:app`

You may want it run on background by using & or other commands. But I recommand using `screen -R box`
