#!/usr/bin/python 
#coding: utf-8
 
import itchat,datetime
from itchat.content import TEXT
import os
import matplotlib.pyplot as plt
 
itchat.auto_login(enableCmdQR = False)
#获取群
roomslist = itchat.get_chatrooms()

# #群名称
# itchat.dump_login_status() # 显示所有的群聊信息，默认是返回保存到通讯录中的群聊
# myroom=itchat.search_chatrooms(name=u'❗️抽奖👍预备群1️⃣') #群聊名称
# gsq=itchat.update_chatroom(myroom[0]['UserName'], detailedMember=True)

# man = 0
# woman = 0
# other = 0

# for c in gsq['MemberList']:
#     if c['Sex'] == 1:
#         man+=1
#     elif c['Sex'] == 2:
#         woman+=1
#     else:
#         other+=1
 
# print('男：',man); 
# print('女：',woman); 
# print('其他：',other); 


# prov_dict, city_dict = {}, {}
# for fri_info in gsq['MemberList']:
#     prov = fri_info['Province']
#     city = fri_info['City']
#     if prov and prov not in prov_dict.keys():
#         prov_dict[prov] = 1
#     elif prov:
#         prov_dict[prov] += 1
#     if city and city not in city_dict.keys():
#         city_dict[city] = 1
#     elif city:
#         city_dict[city] += 1


# # 区域Top10
# prov_dict_top10 = sorted(prov_dict.items(), key=lambda x: x[1], reverse=True)[0:10]
# # 城市Top10
# city_dict_top10 = sorted(city_dict.items(), key=lambda y: y[1], reverse=True)[0:10]

# print(prov_dict_top10)
# print(city_dict_top10)

# prov_nm, prov_num = [], []  # 省会名 + 数量
# for prov_data in prov_dict_top10:
#     prov_nm.append(prov_data[0])
#     prov_num.append(prov_data[1])

# pwd_path = os.path.abspath(os.path.dirname(os.getcwd()))
# desc_full = os.path.join(pwd_path, 'res')
# colors = ['#00FFFF', '#7FFFD4', '#F08080', '#90EE90', '#AFEEEE',
#           '#98FB98', '#B0E0E6', '#00FF7F', '#FFFF00', '#9ACD32']
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# index = range(len(prov_num))
# plt.bar(index, prov_num, color=colors, width=0.5, align='center')

# plt.xticks(range(len(prov_nm)), prov_nm)  # 横坐轴标签
# for x, y in enumerate(prov_num):
#     # 在柱子上方1.2处标注值
#     plt.text(x, y + 1.2, '%s' % y, ha='center', fontsize=10)
# plt.ylabel('省会好友人数')  # 设置纵坐标标签
# prov_title = '微信好友区域Top10'
# plt.show()





# # 保存
# with open('gss.txt','a') as f:
#     for c in gsq['MemberList']:
#         f.write(c['NickName'] + "|" +  c['DisplayName'] + '\n')

# with open('gss.js','a') as j:
#     j.write(str(gsq['MemberList']))