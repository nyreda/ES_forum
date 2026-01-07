import os
import fnmatch
'''
for file1 in os.listdir('../static/img/history/online'):
    if fnmatch.fnmatch(file1, 'online-1-*'):
        print(file1)

list = 'online-2-3.mp4'
print(list[11:])'''
#new = sorted(list,key = lambda i:int(re.match(r'(\d+)',i).group()))
#print(list)



def find_doc_online(paragraph):
    doc_list = []
    simple_list = []
    doc_name = 'online-' + str(paragraph) + '-*'
    for file in os.listdir('./app01/static/img/history/online/'):
        #print('获取含有'+doc_name+'的图片')
        if fnmatch.fnmatch(file, doc_name):
            #print("文件有"+file)
            doc_list.append('img/history/online/'+file)     #每个图片的路径存在列表中
    doc_list = sorted(doc_list)     #对列表进行排序
    #print(doc_list)

    for d in doc_list:
        #print(d)
        #print("格式"+d[30:])
        dictionary = {d:d[30:]}      #写入到字典
        simple_list.append(dictionary)
        #list_all.append(doc_list)
        #print(doc_list)
    #doc_list = sorted(doc_list)
    #print("全部",doc_list)
    return simple_list

