from django.shortcuts import render
from bs4 import BeautifulSoup
from django.http import HttpResponse
from .models import Category, SubCategory, SubGroup, Attribute, Group, Option
import datetime
import requests
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
			if child['class'] == ['l_one']:
				
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


def test(request):
	mask = SubGroup.objects.filter(name= 'زنانه')[0]
	attribute = Attribute.objects.filter(subgroup=mask, name='کشور مبدا برند')
	ops = Option.objects.filter(attribute=attribute)
	return render(request, 'test.html', {'mask' : mask, 'attrs' : attribute, 'ops' : ops})



