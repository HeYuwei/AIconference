import csv

headers = ['name','parent','type','hold_time']
rows = [
        {'name':'arxiv','parent':'arxiv','type':'conf','hold_time':'always'},
        {'name':'aaai','parent':'aaai','type':'conf','hold_time':'always'},
        {'name':'cvpr','parent':'cvpr','type':'conf','hold_time':'always'},
        {'name':'iccv','parent':'iccv','type':'conf','hold_time':'single'},
        {'name':'eccv','parent':'eccv','type':'conf','hold_time':'double'},
        {'name':'ijcai','parent':'ijcai','type':'conf','hold_time':'always'},
        {'name':'icml','parent':'icml','type':'conf','hold_time':'always'},
        {'name':'iclr','parent':'iclr','type':'conf','hold_time':'always'},
        {'name':'nips','parent':'nips','type':'conf','hold_time':'always'},
        {'name':'icme','parent':'icmcs','type':'conf','hold_time':'always'},
        {'name':'mm','parent':'mm','type':'conf','hold_time':'always'},
        {'name':'alt','parent':'alt','type':'conf','hold_time':'always'}
    ]

with open('conf_info.csv','w')as f:
    writer = csv.DictWriter(f, headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
