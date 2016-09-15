from django.shortcuts import render
from bs4 import BeautifulSoup
from django.http import HttpResponse
from .models import Category, SubCategory, SubGroup, Attribute, Group, Option
import datetime
import requests
import certifi
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# Create your views here.

def digi_normalizer(href):
	sub_category_url = 'http://www.digikala.com' + href
	return sub_category_url


def attr_finder(product_page, sub_group_name):
	daurl = digi_normalizer(product_page)
	response = requests.get(daurl, verify=False)
	soup = BeautifulSoup(response.text , 'html.parser')
	div = soup.find('div', {'class' : 'container'})
	
	if div:
		for newchild in div.descendants:
			if newchild.name == 'span':
				if newchild.parent['class'] == ['header']:
					
					product_attr = newchild.text

					subgp = SubGroup.objects.filter(name=sub_group_name)[0]
		
					if not Attribute.objects.filter(name=product_attr, subgroup=subgp):
			
						attrib = Attribute.objects.create(name=product_attr, subgroup=subgp)
					else:
						attrib = Attribute.objects.filter(name=product_attr, subgroup=subgp)[0]

					for child in newchild.parent.descendants:
						
						if child.name == 'li':
							option = child.text
							if len(option) <= 100:
								if not Option.objects.filter(name=option, attribute=attrib):
									Option.objects.create(name=option, attribute=attrib)



def product_page_attr_finder(products_url,sub_category_title, sub_group_name):

	response = requests.get(products_url, verify=False)
	soup = BeautifulSoup(response.text , 'html.parser')
	article = soup.find('article', {'id' : 'dynamicFilter'})
	if article:
		for child in article.descendants:

			if child.name == 'span':
				subcat = SubCategory.objects.filter(name=sub_category_title)[0]
				subgp = SubGroup.objects.filter(name=sub_group_name, subcategory=subcat)[0]
				
				if not Attribute.objects.filter(name=child.text, subgroup=subgp):
					Attribute.objects.create(name=child.text, subgroup=subgp)
				#product_page = digi_normalizer(child['href']) + '#!/tab-techspecs/'
				#attr_finder(product_page,sub_category_title, sub_group_name)



def sub_group_crawler(url, sub_category_title):

	response = requests.get(url, verify=False)
	soup = BeautifulSoup(response.text , 'html.parser')
	rootitem = soup.find('li' , {'class' : 'rootitem2'})
	
	for child in rootitem.descendants:
		if child.name == 'a':

			sub_group_name = child.contents[0].text

			subcategory = SubCategory.objects.filter(name=sub_category_title)[0]

			if not SubGroup.objects.filter(name=sub_group_name, subcategory=subcategory):
				SubGroup.objects.create(name=sub_group_name, subcategory=subcategory)

			products_url = digi_normalizer(child['href'])
			product_page_attr_finder(products_url, sub_category_title, sub_group_name)



#def sub_group_finder():
#	response = requests.get('http://www.digikala.com', verify=False)
#	soup = BeautifulSoup(response.text, 'html.parser')
#	ulowner = soup.find_all('ul', {'class' : 'root'})
#	
#	for tag in ulowner.descendants:
#		
#		if tag.name == ''
#		if not Category.objects.filter(name=box.contents[0].text):
#			Category.objects.create(name=box.contents[0].text)
#
#		for child in box.descendants:
#			if child.name == 'a':
#				category = Category.objects.filter(name=box.contents[0].text)[0]
#				subname = child['title']
#					
#				if not SubCategory.objects.filter(name=subname, category=category):
#					SubCategory.objects.create(name=subname, category=category)
#					
#				sub_group_crawler(digi_normalizer(child['href']), child['title'])





def awesome_spider():

	response = requests.get('http://www.digikala.com', verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	ulowner = soup.find('ul', {'class' : 'root'})

	for child in ulowner.descendants:
		if child.name == 'li':
			if child['class'] == ['l_one'] and child.contents[0].text == 'مادر و کودک':
				
				if not Category.objects.filter(name=child.contents[0]['title']):
					category = Category.objects.create(name=child.contents[0]['title'])
				else:
					category = Category.objects.filter(name=child.contents[0]['title'])[0]
			

				for subchild in child.contents[1].descendants:
					if subchild.name == 'li':
						if subchild['class'] == ['l_two']: # subcategories
						
							if not SubCategory.objects.filter(name=subchild.contents[0].text, category=category):
								subcategory = SubCategory.objects.create(name=subchild.contents[0].text, category=category)
							else:
								subcategory = SubCategory.objects.filter(name=subchild.contents[0].text, category=category)[0]

							for subsubchild in subchild.descendants:
								if subsubchild.name == 'ul':
									for newchild in subsubchild.contents: #groups
										if newchild.name == 'li':
											if newchild['class'] == ['title']:
										
												if not Group.objects.filter(name=newchild.contents[0].text, subcategory=subcategory):
													group = Group.objects.create(name=newchild.contents[0].text, subcategory=subcategory)

												else:
													group = Group.objects.filter(name=newchild.contents[0].text, subcategory=subcategory)[0]

											elif newchild['class'] == ['item']:
												try:
													if not SubGroup.objects.filter(name=newchild.contents[0].text, group=group):

														subgroup = SubGroup.objects.create(name=newchild.contents[0].text, group=group)
														attr_finder(newchild.contents[0]['href'], subgroup.name)
													else:
														subgroup = SubGroup.objects.filter(name=newchild.contents[0].text, group=group)[0]
														attr_finder(newchild.contents[0]['href'], subgroup.name)

												except AttributeError:

													if not SubGroup.objects.filter(name=newchild.contents[1].text, group=group):

														subgroup = SubGroup.objects.create(name=newchild.contents[1].text, group=group)
														attr_finder(newchild.contents[1]['href'], subgroup.name)
													else:

														subgroup = SubGroup.objects.create(name=newchild.contents[1].text, group=group)
														attr_finder(newchild.contents[1]['href'], subgroup.name)
												
														


#										for newborn in subsubchild.parent.descendants:
#											if newborn.name == 'li':
#												if newborn['class'] == ['item']:#subgroup
#													if newborn.contents[0].name == 'a':
#
#														if not SubGroup.objects.filter(name=newborn.contents[0].text, group=group):
#															subgroup = SubGroup.objects.create(name=newborn.contents[0].text, group=group)
#														
#														else:
#															subgroup = SubGroup.objects.filter(name=newborn.contents[0].text, group=group)[0]
###
	#													if not newborn.contents[0].text == 'مشاهده موارد بیشتر':
	#														attr_finder(newborn.contents[0]['href'], subgroup.name)


def web_spider(request):
	if request.method == 'GET':
		awesome_spider()
		return HttpResponse('Done!')





def amazon_normalizer(href):
	subdepturl = 'http://www.findbrowsenodes.com' + href
	return subdepturl


def browse_nodes_first():
	response = requests.get('http://www.findbrowsenodes.com/us', verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	atags = soup.find_all('a', {'class' : 'c_name'})
	
	for atag in atags:
		
		suburl = amazon_normalizer(atag['href'])
		deptname = atag.text
		
		if Category.objects.filter(name=deptname):
			deptid = Category.objects.filter(name=deptname)[0].id
			browse_nodes_second(suburl, deptid)
		
		else:
			
			dept = Category.objects.create(name=deptname)
			browse_nodes_second(suburl, dept.id)

			



def browse_nodes_second(page, deptid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtags = soup.find_all('div', {'class' : 'subll'})
	
	
	for divtag in divtags:
		subdeptname = divtag.contents[0].text
		newhref = divtag.contents[0]['href']
		newurl = amazon_normalizer(newhref)
	
		if SubCategory.objects.filter(name=subdeptname, category=Category.objects.get(id=deptid)):
			browse_nodes_third(newurl, SubCategory.objects.filter(name=subdeptname, category=Category.objects.get(id=deptid))[0].id)
		else:
			subcat = SubCategory.objects.create(name=subdeptname, category=Category.objects.get(id=deptid))
			browse_nodes_third(newurl, subcat.id)



def browse_nodes_third(page, subdeptid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtags = soup.find_all('div', {'class' : 'subll'})
	
	
	for divtag in divtags:
		groupname = divtag.contents[0].text
		newhref = divtag.contents[0]['href']
		newurl = amazon_normalizer(newhref)

		if not Group.objects.filter(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid)):
			subcat = Group.objects.create(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid))
			browse_nodes_fourth(newurl, subcat.id)	
		
		else:
			subcat = Group.objects.filter(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid))[0]
			browse_nodes_fourth(newurl, subcat.id)



def browse_nodes_fourth(page, subdeptid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtags = soup.find_all('div', {'class' : 'subll'})

	attrpage = soup.find('div', {'class' : 'amz a1-amz'})
	dapage = attrpage.contents[0]['href']
	for divtag in divtags:
		subgroupname = divtag.contents[0].text
		newhref = divtag.contents[0]['href']
		newurl = amazon_normalizer(newhref)

		if not SubGroup.objects.filter(name=subgroupname, group=Group.objects.get(id=subdeptid)):
			subcat = SubGroup.objects.create(name=subgroupname, group=Group.objects.get(id=subdeptid))
			amazon_attr_finder(dapage, subcat.id)

		else:
			subcat = SubGroup.objects.filter(name=subgroupname, group=Group.objects.get(id=subdeptid))[0]
			amazon_attr_finder(dapage, subcat.id)





def amazon_attr_finder(dapage, subgpid):
	
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	
	attr_resp = requests.get(dapage, verify=True)
	newsoup = BeautifulSoup(attr_resp.text, 'html.parser')
	heads = newsoup.find_all('h2', {'class':''})
	subcat = SubGroup.objects.get(id=subgpid)

	for head in heads:
		wade = head
		head = head.text
		if 'Shop' not in head and 'Customer' not in head and 'Price' not in head and 'Discount' not in head and 'Seller' not in head and 'Amazon' not in head and 'Eligible' not in head and 'Packaging' not in head and 'New Arrivals' not in head and 'Availability' not in head: 
			attrname = head
			ul = wade.next_sibling.next_sibling

			if Attribute.objects.filter(name=attrname, subgroup=subcat):
				attrib = Attribute.objects.filter(name=attrname, subgroup=subcat)[0]
			else:
				attrib = Attribute.objects.create(name=attrname, subgroup=subcat)

			for tag in ul.descendants:

				if tag.name == 'span' and tag['class'] == ['refinementLink']:
					optname = tag.text

					if not Option.objects.filter(name=optname, attribute=attrib):
						Option.objects.create(name=optname, attribute=attrib)


def browse_amazon_nodes(request):
	browse_nodes_first()
	return HttpResponse('OK')	



def tesco_normalizer(href):
	newurl = 'http://www.tesco.com' + href
	return newurl



def tesco_first():
	response = requests.get('http://www.tesco.com/direct/?sc_cmp=ref*dchp*stc*tab*tab&utm_source=dchp&utm_medium=tab&utm_campaign=tab', verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	htags = soup.find_all('h2', {'class' : 'department-title'})	

	for htag in htags:

		suburl = tesco_normalizer(htag.parent['href'])
		deptname = htag.text
		
		if Category.objects.filter(name=deptname):
			deptid = Category.objects.filter(name=deptname)[0].id
			if deptname == 'Toys' or deptname == 'Home' or 'Car' in deptname:
				tesco_second(suburl, deptid)
		
		else:
			
			dept = Category.objects.create(name=deptname)
			if deptname == 'Toys' or deptname == 'Home' or 'Car' in deptname:
				tesco_second(suburl, dept.id)


def tesco_second(suburl, deptid):

	response = requests.get(suburl, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtag = soup.find('div', {'class' : 'menu'})	

	#if divtag:
	#	for tag in divtag.descendants:
	#		if tag.name == 'li':

	#			for newtag in tag.descendants:
	#				if newtag.name == 'a':
	#					newhref=newtag['href']
	#					subdeptname = newtag.contents[1].text
	#
	#					newurl = tesco_normalizer(newhref)

	
	#					if SubCategory.objects.filter(name=subdeptname, category=Category.objects.get(id=deptid)):
	#						tesco_third(newurl, SubCategory.objects.filter(name=subdeptname, category=Category.objects.get(id=deptid))[0].id)
	#					else:
	#						subcat = SubCategory.objects.create(name=subdeptname, category=Category.objects.get(id=deptid))
	#						tesco_third(newurl, subcat.id)


	if soup.find('div', {'class' : 'coded-left-nav'}):

		divtags = soup.find_all('div', {'class' : 'coded-left-nav'})
		for divtag in divtags:
			for newtag in divtag.descendants:
				
				if newtag.name == 'h2':

					subdeptname = newtag.text

					if SubCategory.objects.filter(name=subdeptname, category=Category.objects.get(id=deptid)):
						
						subct = SubCategory.objects.filter(name=subdeptname, category=Category.objects.get(id=deptid))
					else:
						subct = SubCategory.objects.create(name=subdeptname, category=Category.objects.get(id=deptid))
						


				elif newtag.name == 'a':
					newhref = newtag['href']
					gpname = newtag.contents[0]
					newurl = tesco_normalizer(newhref)

					if Group.objects.filter(name=gpname, subcategory=subct):
						grp = Group.objects.filter(name=gpname, subcategory=subct)[0]
						tesco_fourth(newurl, grp.id)

					else:
						grp = Group.objects.create(name=gpname, subcategory=subct)
						tesco_fourth(newurl, grp.id)						


def tesco_third(page, subdeptid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtag = soup.find('div', {'class' : 'menu'})	

	if divtag:
		for tag in divtag.descendants:
			if tag.name == 'li':

				for newtag in tag.descendants:
					if newtag.name == 'a':
						newhref=newtag['href']
						groupname = newtag.contents[1].text
						newurl = tesco_normalizer(newhref)

						if not Group.objects.filter(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid)):
							subcat = Group.objects.create(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid))
							tesco_fourth(newurl, subcat.id)	
		
						else:
							subcat = Group.objects.filter(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid))[0]
							tesco_fourth(newurl, subcat.id)


	elif soup.find('div', {'id' : 'product-categories'}):

		divtag = soup.find('div', {'id' : 'product-categories'})

		for newtag in divtag.descendants:
			if newtag.name == 'a':
				newhref=newtag['href']
				groupname = newtag.contents[0]
				newurl = tesco_normalizer(newhref)

				if not Group.objects.filter(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid)):
					subcat = Group.objects.create(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid))
					tesco_fourth(newurl, subcat.id)	
		
				else:
					subcat = Group.objects.filter(name=groupname, subcategory=SubCategory.objects.get(id=subdeptid))[0]
					tesco_fourth(newurl, subcat.id)



def tesco_fourth(page, groupid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtag = soup.find('div', {'id' : 'product-categories'})	

	if divtag:
		for tag in divtag.descendants:

			if tag.name == 'a':

				newhref=tag['href']
				subgroup = tag.contents[0]
				newurl = tesco_normalizer(newhref)
				group = group=Group.objects.get(id=groupid)
						
				if not SubGroup.objects.filter(name=subgroup, group=group):
					subgroup = SubGroup.objects.create(name=subgroup, group=group)
					tesco_attribute(newurl, subgroup.id)

				else:
					subgroup = SubGroup.objects.filter(name=subgroup, group=group)[0]
					tesco_attribute(newurl, subgroup.id)							


	else:
		group = group=Group.objects.get(id=groupid)

		if not SubGroup.objects.filter(name=group.name, group=group):
			subgroup = SubGroup.objects.create(name=group.name, group=group)
			tesco_attribute(page, subgroup.id)
		else:
			subgroup = SubGroup.objects.filter(name=group.name, group=group)[0]			
			tesco_attribute(page, subgroup.id)



def tesco_attribute(page, subgroupid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtags = soup.find_all('div', {'class' : 'filter-filterGroup'})
	subgroup = SubGroup.objects.get(id=subgroupid)

	for divtag in divtags:
		for tag in divtag.descendants:
			if tag.name == 'h3':
				attrname = tag.text
				
				if 'Price' not in attrname and 'Rating' not in attrname and 'Sold' not in attrname:
					
					if not Attribute.objects.filter(name=attrname, subgroup=subgroup):
						attr = Attribute.objects.create(name=attrname, subgroup=subgroup)
					else:
						attr = Attribute.objects.filter(name=attrname, subgroup=subgroup)[0]

			if tag.name == 'a':
				optionname = tag.contents[0]
				check = tag.parent.parent.parent.parent.contents[1].text
				
				if 'Price' not in check and 'Rating' not in check and 'Sold' not in check:

					if not Option.objects.filter(name=optionname, attribute=attr):
						Option.objects.create(name=optionname, attribute=attr)


def tesco_runner(request):
	tesco_first()
	return HttpResponse('OK')



def edit_tesco(request):
	for category in Category.objects.all():
		category.name = category.name.replace('  ', '')
		category.name = category.name.replace('\n', '')
		category.save()

	for category in SubCategory.objects.all():
		category.name = category.name.replace('  ', '')
		category.name = category.name.replace('\n', '')
		category.save()

	for category in Group.objects.all():
		category.name = category.name.replace('  ', '')
		category.name = category.name.replace('\n', '')
		category.save()

	for category in SubGroup.objects.all():
		category.name = category.name.replace('  ', '')
		category.name = category.name.replace('\n', '')
		category.save()

	for category in Attribute.objects.all():
		category.name = category.name.replace('  ', '')
		category.name = category.name.replace('\n', '')
		category.save()

	for category in Option.objects.all():
		category.name = category.name.replace('  ', '')
		category.name = category.name.replace('\n', '')
		category.save()

	return HttpResponse('Done')



def grocery_one():

	response = requests.get("http://www.tesco.com/groceries/", verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtags = soup.find_all('div', {'class' : 'fiveStamp'})
	if not Category.objects.filter(name='Groceries'):
		category = Category.objects.create(name='Groceries')
	else:
		category = Category.objects.filter(name='Groceries')[0]

	for divtag in divtags:
		for tag in divtag.descendants:
			if tag.name == 'a':
				subcat = tag.contents[1].text
				page = tag['href']
				subcat = subcat.replace('  ','')
				subcat = subcat.replace('\n','')

				if not SubCategory.objects.filter(name=subcat, category=category):
					sub = SubCategory.objects.create(name=subcat, category=category)
					grocery_two(page, sub.id)

				else:
					sub = SubCategory.objects.filter(name=subcat, category=category)[0]
					grocery_two(page, sub.id)


def grocery_two(page, subcatid):
	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtag = soup.find('ul', {'class' : 'tertNav first'})

	for tag in divtag.descendants:
		if tag.name == 'a':
			page = tag['href']
			group = tag.text
			subcategory = SubCategory.objects.get(id=subcatid)
			if not Group.objects.filter(name=group, subcategory=subcategory):
				group = Group.objects.create(name=group, subcategory=subcategory)
				grocery_three(page, group.id)

			else:
				group = Group.objects.filter(name=group, subcategory=subcategory)[0]
				grocery_three(page, group.id)


def grocery_three(page,groupid):

	response = requests.get(page, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divtag = soup.find('div', {'class' : 'section clearfix'})

	for tag in divtag.descendants:
		if tag.name == 'a':

			subgroup = tag.text
			group = Group.objects.get(id=groupid)

			if not SubGroup.objects.filter(name=subgroup, group=group):
				group = SubGroup.objects.create(name=subgroup, group=group)


def tesco_grocery(request):
	grocery_one()
	return HttpResponse('Done')


def target_attr_finder(page):

	r = requests.get(page, verify=False)
	soup = BeautifulSoup(r.text, 'html.parser')



def target(request):
	with open('crawler/target.json') as target:  
		data = json.load(target)
	for category in data['childnodes']:
		cat = Category.objects.create(name=category['title'])
    	
		for subcategory in category['childnodes']:
			subcat = SubCategory.objects.create(name=subcategory['title'], category=cat)

			for group in subcategory['childnodes']:
				gp = Group.objects.create(name=group['title'], subcategory=subcat)

				for subgroup in group['childnodes']:
					subgp = SubGroup.objects.create(name=subgroup['title'], group=gp)


	return HttpResponse('OK')  