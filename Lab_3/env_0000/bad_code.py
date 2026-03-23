import os
import sys
import json
from datetime import datetime
import math


# Zle sformatowana funkcja - brakuje spacji, zla ilosc pustych linii
def calculate_discount(price,discount_percent):
    if discount_percent>100:
        return 0
    if discount_percent<0:
        return price
    discount_amount=price*discount_percent/100
    final_price=price-discount_amount
    return final_price


def get_current_timestamp():
    now=datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# Zbyt dlugie linie i nadmiarowe spacje
def describe_product( product_name,   price,   category  ):
    timestamp=get_current_timestamp()
    description="Produkt: "+product_name+"  |  Cena: "+str(price)+" PLN  |  Kategoria: "+category+"  |  Czas: "+timestamp
    return description


class ProductCatalog:
    def __init__(self,name):
        self.name=name
        self.products=[]

    def add_product(self,product_name,price,category):
        product={"name":product_name,"price":price,"category":category,"added_at":get_current_timestamp()}
        self.products.append(product)

    def get_cheapest( self ):
        if not self.products:
            return None
        cheapest=min(self.products,key=lambda p:p["price"])
        return cheapest

    def to_json( self ):
        return json.dumps({"catalog":self.name,"products":self.products},indent=2,ensure_ascii=False)


def main():
    catalog=ProductCatalog("Sklep testowy")
    catalog.add_product("Laptop",3499.99,"Elektronika")
    catalog.add_product("Kawa",24.99,"Spozywcze")
    catalog.add_product("Ksiazka",39.90,"Edukacja")

    print(catalog.to_json())

    cheapest=catalog.get_cheapest()
    print("Najtanszy produkt:",cheapest["name"],"za",cheapest["price"],"PLN")

    discounted=calculate_discount(cheapest["price"],15)
    print("Po rabacie 15%:",round(discounted,2),"PLN")


if __name__=="__main__":
    main()
