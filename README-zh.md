# boxHelper2

[English](https://github.com/SpereShelde/boxHelper2/blob/master/README.md)

这是一个基于Python3开发的新版boxHelper。与老版本不同，新版本致力于兼容所有网站而不需要针对特定网站专门开发。BoxHelper2依赖于RSS获取种子信息。

boxHelper2分为两个主要模块，分别是抓取模块和控制模块，并配有网页控制台。目前抓取模块已经完成（手上只有mt和sky的号，其他网站没有测试）。控制模块在构思中，比预想的难实现，所以暂时仅生产RSS，可以交由其他能处理RSS的软件控制，比如ruTorrent和Flexget。

## 用法

### 环境
apt install python3

apt install python3-pip

pip3 install virtualenv

### 安装

#### 下载

`wget -O 'boxHelper2.zip' 'https://github.com/SpereShelde/boxHelper2/archive/master.zip'`

#### 解压

`unzip boxHelper2.zip`

#### Python 虚拟环境

`cd boxHelper2 && mkdir ENV && cd ENV`

`source ./bin/activate`

#### 安装依赖

`cd .. && pip3 install -r requirements.txt`

####  编写配置文件

`nano config.ini`

sites_amount 即需要监控的页面个数，需要有对应数量的配置组

url 即监控页面地址

cookie 需要填写键值对格式，可以通过 Edit My Cookie插件获取也可通过开发者模式获取

rss 即对应监控页面的RSS地址

strength 目前支持两种强度，10代表仅获取RSS中的种子信息，20代表获取监控页面所有的种子信息。两种强度均可以判断种子是否免费。区别在于强度10不能（应该）抓取促销老种，强度20可以。

cycle 即循环抓取时间

#### 运行

`gunicorn -b 0.0.0.0:12020 app:app`

你可以通过使用 & 等命令后台运行boxHelper2，但是我推荐使用 `screen -R box`

### 使用

运行后会在本地的12020端口生成简易控制台。在RSS页面，目前支持五个可选参数，num控制数量，pro控制是否免费(10为Free)，show控制种子大小的单位(01234位别为B，KB，MB，GB，TB)，low和high控制种子大小的范围(单位是B)

比如：http://127.0.0.1:12020/rss?num=20&pro=10&show=3&low=10737418240&high=21474836480 代表获取20个大小在10-20GB的Free种以GB单位显示

## 后续开发

- RSS交互控制面板
- 控制模块
