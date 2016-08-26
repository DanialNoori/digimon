from django.db import models

# Create your models here.

class Category(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)


	def __str__(self):
		return self.name



class SubCategory(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)
	category = models.ForeignKey(Category, blank=True, null=True)

	def __str__(self):
		return self.name


class Group(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)
	subcategory = models.ForeignKey(SubCategory, blank=True, null=True)

	def __str__(self):
		return self.name


class SubGroup(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)
	group = models.ForeignKey(Group, blank=True, null=True)

	def __str__(self):
		return self.name


class Attribute(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)
	subgroup = models.ForeignKey(SubGroup, blank=True, null=True)

	def __str__(self):
		return self.name


class Option(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)
	attribute = models.ForeignKey(Attribute, blank=True, null=True)

	def __str__(self):
		return self.name
