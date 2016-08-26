from django.shortcuts import render
from bs4 import BeautifulSoup
from django.http import HttpResponse
from .models import Category, SubCategory, SubGroup, Attribute
import datetime
import requests
# Create your views here.

def digi_normalizer(href):
	sub_category_url = 'http://www.digikala.com' + href
	return sub_category_url


def attr_finder(product_page,sub_category_title, sub_group_name):
	response = requests.get(product_page, verify=False)
	soup = BeautifulSoup(response.text , 'html.parser')
	spans = soup.find_all('span', {'class' : 'technicalspecs-title'})
	for span in spans:
		
		product_attr = span.text
		subcat = SubCategory.objects.filter(name=sub_category_title)
		subgp = SubGroup.objects.filter(name=sub_group_name, subcategory=subcat)
		if not Attribute.objects.filter(name=product_attr, subgroup=subgp):
			Attribute.objects.create(name=product_attr, subgroup=subgp)
		


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



def sub_group_finder():
	response = requests.get('http://www.digikala.com', verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	boxes = soup.find_all('div', {'class' : 'box'})
	
	for box in boxes:
			
		if not Category.objects.filter(name=box.contents[0].text):
			Category.objects.create(name=box.contents[0].text)

		for child in box.descendants:
			if child.name == 'a':
				category = Category.objects.filter(name=box.contents[0].text)[0]
				subname = child['title']
					
				if not SubCategory.objects.filter(name=subname, category=category):
					SubCategory.objects.create(name=subname, category=category)
					
				sub_group_crawler(digi_normalizer(child['href']), child['title'])



def web_spider(request):
	if request.method == 'GET':
		sub_group_finder()
		return HttpResponse('Done!')
