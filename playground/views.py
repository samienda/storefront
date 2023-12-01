from django.db.models.fields import DecimalField
from django.shortcuts import render
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
# Create your views here.
# request -> response
# request handler



def say_hello(request):

    return render(request, 'hello.html', {'name': 'Sami'})
