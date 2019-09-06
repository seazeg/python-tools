import os
import os.path
import sys
import shutil

#需整理的文件后缀数组
extList = [['txt','Docs'],['doc','Docs'],['docx','Docs'],['xls','Docs'],['xlsx','Docs'],['csv','Docs'],['mp3','Music'],['wma','Music'],['mid','Music'],['wav','Music'],['avi','Movie'],['mp4','Movie'],['rmvb','Movie'],['rm','Movie'],['mov','Movie'],['wmv','Movie'],['mkv','Movie'],['flv','Movie'],['3gp','Movie'],['png','Pictures'],['gif','Pictures'],['jpeg','Pictures'],['svg','Pictures'],['bmp','Pictures'],['psd','Pictures'],['tiff','Pictures'],['ai','Pictures'],['cdr','Pictures'],['raw','Pictures'],['eps','Pictures'],['webp','Pictures'],['ico','Pictures'],['icns','Pictures'],['jpg','Pictures'],['pdf','Books']]

def desc():
    print("\n********************************************************************")
    print('''
        ███████╗██╗   ██╗ █████╗ ███╗   ██╗    ██████╗ 
        ██╔════╝██║   ██║██╔══██╗████╗  ██║   ██╔════╝ 
        █████╗  ██║   ██║███████║██╔██╗ ██║   ██║  ███╗
        ██╔══╝  ╚██╗ ██╔╝██╔══██║██║╚██╗██║   ██║   ██║
        ███████╗ ╚████╔╝ ██║  ██║██║ ╚████║██╗╚██████╔╝
        ╚══════╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝ 
                                                    
        ''')
    print("文件归类器")
    print("\n********************************************************************")


def sort(dirpath):
    for parent,dirnames,filenames in os.walk(dirpath): 
        for filename in filenames:    
            #文件所在绝对路径
            oldpath = os.path.join(parent,filename)
            fileExt = filename.split(".")[1]
            for ext in extList:
                if(fileExt==ext[0]):
                    #新建文件夹路径
                    newdir = os.getcwd()+'/'+ext[1]
                    #新建文件夹
                    mkdir(newdir)
                    #移动文件
                    shutil.move(oldpath,newdir+'/'+filename)


def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    # 判断路径是否存在
    isExists=os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path) 
        print(path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path+' 目录已存在')
        return False
 

if __name__ == '__main__':
    desc()
    sort(os.getcwd())
    print('整理完成END')