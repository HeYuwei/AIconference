import csv

headers = ['name','parent','type','hold_time','database']
rows = [
        {'name':'arxiv','parent':'arxiv','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'aaai','parent':'aaai','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'cvpr','parent':'cvpr','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'iccv','parent':'iccv','type':'conf','hold_time':'single','database':'dblp'},
        {'name':'eccv','parent':'eccv','type':'conf','hold_time':'double','database':'dblp'},
        {'name':'ijcai','parent':'ijcai','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'icml','parent':'icml','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'iclr','parent':'iclr','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'nips','parent':'nips','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'icme','parent':'icmcs','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'mm','parent':'mm','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'mmi','parent':'mmi','type':'journal','hold_time':'always','database':'dblp'},
        {'name':'alt','parent':'alt','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'tmi','parent':'tmi','type':'journals','hold_time':'always','database':'dblp'},
        {'name':'miccai','parent':'miccai','type':'conf','hold_time':'always','database':'dblp'},
        {'name':'jama','parent':'jama','type':'journals','hold_time':'always','database':'medhub'},
        {'name':'nbe','parent':'Nat Biomed Eng','type':'journals','hold_time':'always','database':'medhub'},
        {'name':'nm','parent':'Nat Methods','type':'journals','hold_time':'always','database':'medhub'},
        {'name':'nm','parent':'Nat Mach Intell','type':'journals','hold_time':'always','database':'medhub'},

    ]

with open('conf_info.csv','w')as f:
    writer = csv.DictWriter(f, headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)