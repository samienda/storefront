from typing import Any
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from . import models
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from tags.models import TaggedItem
# Register your models here.


class IventoryFiltter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('>=10', 'OK')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        if self.value() == '>=10':
            return queryset.filter(inventory__gte=10)


class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']

    actions = ['clear_inventory']
    search_fields = ['title']

    list_display = ['title', 'unit_price',
                    'inventory_status', 'inventory', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', IventoryFiltter]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='clear inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} products successfully updated',
            messages.SUCCESS,

        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'view_orders']
    list_editable = ['membership']
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='view_orders')
    def view_orders(self, customer):
        url = (reverse('admin:store_order_changelist')
               + '?'
               + urlencode({
                   'customer_id': str(customer.id)
               }))
        return format_html('<a href="{}">{}</a>', url, customer.view_orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(view_orders=Count('order'))


class OrderItemInline(admin.StackedInline):
    model = models.OrderItem
    autocomplete_fields = ['product']


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]

    list_display = ['id', 'placed_at', 'customer_name']

    list_select_related = ['customer']

    def customer_name(self, order):
        return order.customer


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
                   'collection__id': str(collection.id)
               }))
        return format_html('<a href="{}" >{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))
