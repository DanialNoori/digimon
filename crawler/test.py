import json

cat = 0
subcat = 0
gp = 0
subgp = 0

with open('target.json') as target:  
	data = json.load(target)
	
	for category in data['childnodes']:
		cat +=1
    	
		for subcategory in category['childnodes']:
			subcat += 1

			for group in subcategory['childnodes']:
				gp += 1				

				for subgroup in group['childnodes']:
					subgp +=1	

	print(str(cat) + '/' + str(subcat) + '/' + str(gp) + '/' + str(subgp))