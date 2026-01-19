from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose,TakeFirst

class ChocolateProductLoader(ItemLoader):
    default_output_processor = TakeFirst()
    price_in = MapCompose(
        str.strip,
        lambda x: x.replace("£", "")
    )
    url_in = MapCompose(lambda x : "www.chocolate.co.uk"+x)
    
    
    
    