import re
import os
import shutil

import tool



def clean_filename(filename):
    # 替换非法字符为下划线
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 去除开头/结尾的空格和句点
    cleaned = cleaned.strip(' .')
    return cleaned
# path = [i for i in os.listdir('.\\') if i.endswith('.json') and i.find('_detail_') != -1]
# print(path)
# for json_path in path:
#     data = tool.read_json(json_path)
#     for item in range(len(data)):
#         data[item]['pdf_filename'] = clean_filename(data[item]['pdf_filename'].replace('<-sup>', '').replace('<-sub>', '').replace('<sup>', '').replace('<sub>', '').replace('</sup>', '_').replace('</sub>', '_'))
#         data[item]['pdf_storage_path'] = 'tjpdf/'+data[item]['pdf_filename']
#     tool.write_json(json_path,data)
#
# for json_path in path:
#     data = tool.read_json(json_path)
#     new_data = []
#     new_data_name = []
#     for item in data:
#         if item['pdf_filename'] not in new_data_name:
#             new_data.append(item)
#             new_data_name.append(item['pdf_filename'])
#         else:
#             print(item['pdf_filename'])
#     tool.write_json(json_path , new_data)


def count_file():
    path_pdf  = [os.path.join(r'C:\Users\Administrator\Downloads',i) for i in os.listdir(r'C:\Users\Administrator\Downloads') if i.endswith('.pdf')]
    path = [i for i in os.listdir('.\\') if i.endswith('.json') and i.find('_detail_') != -1]
    for j in path:
        data = tool.read_json(j)
        data_pdf = [i['pdf_filename'] for i in data]
        for i in path_pdf:
            if i.split('\\')[-1] in data_pdf:
                shutil.move(i,i.replace('\\Downloads','\\Downloads\\dhu'))

def fix_file():
    path_pdf  = [os.path.join(r'C:\Users\Administrator\Downloads\dhu',i) for i in os.listdir(r'C:\Users\Administrator\Downloads\dhu') if i.endswith('.pdf')]
    path = [i for i in os.listdir('.\\') if i.endswith('.json') and i.find('_detail_') != -1]
    count_num = 0
    for j in path:
        data = tool.read_json(j)
        new_data = []
        print('旧数据数量：',len(data))
        for i in data:
            for pdf_file in path_pdf:
                if pdf_file.split('\\')[-1] == i['pdf_filename']:
                    new_data.append(i)
        print('新数据数量：',len(new_data))
        count_num += len(new_data)
        tool.write_json(j,new_data)
    print('最终数量：',count_num)

def count():
    path = [i for i in os.listdir('.\\') if i.endswith('.json') and i.find('_detail_') != -1]
    new_data = []
    for i in path:
        data = tool.read_json(i)
        for j in data:
            new_data.append(j)
    tool.write_json('dhu_detail.json',new_data)
count()
