## 依赖安装说明
### 1. pyshark 依赖于系统安装的 Wireshark/tshark，所以还需要在系统层面安装这些工具：
对于 Ubuntu/Debian 系统：
```
sudo apt-get install wireshark tshark
```
对于 MacOS 系统：
```
brew install wireshark
```
对于 CentOS/RHEL 系统： 
```
sudo yum install wireshark tshark
```

### 2. 在某些系统上，可能需要给予用户抓包权限：
```
# 将当前用户添加到 wireshark 组
sudo usermod -a -G wireshark $USER

# 或者直接设置 cap_net_raw 权限
sudo setcap cap_net_raw,cap_net_admin+eip $(which dumpcap)
```

### 3.安装依赖库：
```
pip install -r requirements.txt
```

### 4.运行脚本：
```
python main.py
```


