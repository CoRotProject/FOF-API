import pandas as pd
import json


data_df = pd.DataFrame({
   'id':       [49, 46, 44, 50, 51, 47, 45, 48, 52, 53, 54, 56, 57],
   'parent_id': [0, 49, 46, 44, 50, 51, 47, 45, 48, 51, 51, 0, 54],
   'name': ['inConv1', 'Presencepalette1','NumeroPalette1', 'OutConv1','inConv2',\
        'Presencepalette2', 'NumeroPalette2', 'ApresBranrobotino', 'OutConv2', \
            'aiguillageoff','aiguillageone','inrobotino','outrobotino'],
    'distance': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0 ,0],
    'last_value': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0 ,0],
})

def get_childrens(df, parent_id):
    data = df[df["parent_id"] == parent_id].apply(lambda row: {"id": row["id"],
          "name": row["name"],
          "distance": row["distance"],
          "last_value": row["last_value"],
          "child": []}, axis=1)
    data_list = data.tolist() if not data.empty else []
    for i, d in enumerate(data_list):
        d["child"] = get_childrens(df, d['id'])
    return data_list

import json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump({"child": get_childrens(data_df, 0)}, f, ensure_ascii=False, indent=2)



with open('data.json') as json_file:
    data = json.load(json_file)

list = []
def get_the_list(var):
    l=len(var)
    for i in range(0,l):
        list.append([var[i]['id'],var[i]['name'],var[i]['last_value'],var[i]['distance']]) 
        get_the_list(var[i]["child"])

get_the_list(data["child"])
print(list)