import shutil,os

#替换
def replaceKey(filepath,old,new):
    with open(filepath, 'r+', encoding='UTF-8') as f:
        d = f.read()
        t = d.replace(old, new)
        f.seek(0, 0)
        f.write(t)

#文件操作函数
def fileHandle(name,old,new):
    #复制整个目录
    shutil.copytree(os.getcwd()+'/diy',os.getcwd()+'/'+name)
    work_dir = os.getcwd()+'\\'+name
    #遍历所有文件
    for parent, dirnames, filenames in os.walk(work_dir,  followlinks=True):
        for filename in filenames:
            #文件路径
            file_path = os.path.join(parent, filename)
            #替换函数
            replaceKey(file_path,old,new)
            # print('文件名：%s' % filename)
            # print('文件完整路径：%s\n' % file_path)


#读取配置文件
def getConfig():
    im = open('import.txt','w')
    rc = open('routeCenter.txt','w')
    sid = open('siteId.txt','w')
    with open('config.conf','r', encoding='UTF-8') as f:
        for line in f:
            fileHandle(line.split('|')[0].strip(),line.split('|')[1].strip(),line.split('|')[2].strip());
            #写入import路由列表
            im.writelines('import '+ line.split('|')[0].strip() + 'Map from ./' + line.split('|')[0].strip() + '\n');
            rc.writelines(',' + line.split('|')[0].strip() + 'Map.routes');
            sid.writelines(line.split('|')[0].strip()+':'+line.split('|')[3].strip()+',\n')

# 入口
if __name__=='__main__':
    input('>回车后开始生成')
    getConfig()
    print('>生成成功')
