# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests
from decimal import Decimal
from scrapy.exceptions import DropItem
import mysql.connector 
class CurrencyPipeline:
    pass
   
class PriceToUSDPipeline:
    
    url = "https://open.er-api.com/v6/latest/GBP"
    response = requests.get(url, timeout=10)
    data = response.json()
    gbpToUsdRate = Decimal(str(data["rates"]["USD"]))
    def process_item(self,item,spider):
        adapter = ItemAdapter(item)
        
        if adapter.get('price') and adapter.get("currency") == "GBP":
            decimalPrice = Decimal(adapter['price'])
            adapter['price'] = (self.gbpToUsdRate * decimalPrice).quantize(Decimal("0.00"))
            adapter["currency"] = "USD"
            return item
        
        else:
            raise DropItem(f"Missing price in {item}")
        
class DuplicatesPipeline:
    
        def __init__(self):
            self.names_seen = set() 
        def process_item(self,item,spider):
            adapter = ItemAdapter(item)
            if adapter['name'] in self.names_seen:
                raise DropItem(f"Duplicate item found: {item!r}")
            else: 
                self.names_seen.add(adapter["name"])
                return item
            
            
class SaveToMysqlPipeline(object):
    def __init__(self):
        self.create_connection()
        
        
    def create_connection(self):
        self.connection = mysql.connector.connect(
            host ="localhost",
            user="root",
            password = "mysql123",
            database = "chocolateDB"
        )
        self.curr = self.connection.cursor()
        
    def process_item(self,item,spider):
        self.store_db(item)
        return item
    
    def store_db(self, item):
        adapter = ItemAdapter(item)

        values = (
        adapter.get("name"),
        str(adapter.get("price")),
        adapter.get("currency"),
        adapter.get("url")
        )

        self.curr.execute(
        """
        INSERT INTO chocolate_products (name, price, currency, url)
        VALUES (%s, %s, %s, %s)
        """,
        values
        )

        self.connection.commit()

            
        