# pygps
GPS前置机框架
安装：
``` shell
git clone https://github.com/sillyemperor/pygps.git
cd pygps
python setup.py install
```

启动：
```
python -m pygps.server 协议名称 数据库连接字符串 -P TCP/UDP -p 监听端口
```

例如：
```
python -m pygps.server A5 "DRIVER={SQL Server};SERVER=localhost,3433;DATABASE=my_gps;UID=sa;PWD=123456" -P UDP -p 8800
```

