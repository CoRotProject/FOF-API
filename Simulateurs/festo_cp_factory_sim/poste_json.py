import pandas as pd
import io
import json
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


poste_man2 = pd.DataFrame(
    {
        'id':           [1, 2, 3, 4, 5, 6, 7, 8,8, 9,10,11],
        'parent_id':    [0, 1, 2, 3, 4, 5, 6, 7,10,8,0,7],
        'type': ['in_belt','pres_RFID','RFID','out_belt','in_belt','pres_RFID','RFID','cap_sen','cap_sen','out_belt','cap_sen','cap_sen',],
        'name': ['in_belt1', 'pres_RFID1', 'RFID1', 'out_belt1', 'in_belt2', 'pres_RFID2', 'RFID2','cap_sen_belt2','cap_sen_belt2','out_belt2','int_half_belt2','out_half_belt2'],
        'distance': [0.0, 0.774, 0.0, 0.38, 0.024, 0.22, 0.0, 0.665, 0.35, 0.295, 0.0,  0.5]
    }
)

def get_childrens(df, parent_id):
    data = df[df["parent_id"] == parent_id].apply(lambda row: {"id": row["id"],
          "name": row["name"],
          "type": row["type"],
          "distance": row["distance"],
          }, axis=1)
    data_list = data.tolist() if not data.empty else []
    for i, d in enumerate(data_list):
        d["child"] = get_childrens(df, d['id'])
    return data_list


with io.open('poste_man2.json', 'w', encoding='utf8') as outfile:
    '''str_ = json.dumps(get_childrens(data_df, 0),
                      indent=4, sort_keys=True,
                      separators=(',', ': '), ensure_ascii=False)'''
    str_ = json.dumps({"poste_man2": get_childrens(poste_man2, 0)}, indent=2)
    outfile.write(to_unicode(str_))



print(json.dumps({"post_man2": get_childrens(poste_man2, 0)}, indent=2))
