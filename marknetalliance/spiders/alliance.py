import scrapy
import pandas as pd
df = pd.read_csv('F:\Web Scraping\Golabal\keywords.csv')
base_url = 'https://www.marknetalliance.com/search/lots/all-sales/ending-soon/all-categories/all-locations?terms={}&page=1&items=48'

class AllianceSpider(scrapy.Spider):
    name = 'alliance'
    def start_requests(self):        
        for index in df:            
            yield scrapy.Request(base_url.format(index),cb_kwargs={'index':index})

    def parse(self, response, index):
        """Pagination"""
        total_pages = response.xpath("//ul[@class='pagination']/li[last()]/a/text()").get()        
        current_page = response.css("li.active a::text").get()        
        url = response.url           
        if total_pages == '...':
            pages = response.xpath("//ul[@class='pagination']/li[last()-1]/a/text()").get()
            if pages and current_page:
                if int(current_page) ==1:
                    for i in range(2, int(pages)+2):                
                        min = 'page='+str(i-1)
                        max = 'page='+str(i)
                        url = url.replace(min,max) 
                        # print("If",index,url)                   
                        yield response.follow(url, cb_kwargs={'index':index})
        else:
            if total_pages and current_page:
                if int(current_page) ==1:
                    for i in range(2, int(total_pages)+1):                
                        min = 'page='+str(i-1)
                        max = 'page='+str(i)
                        url = url.replace(min,max) 
                        # print("Else",index,url)                   
                        yield response.follow(url, cb_kwargs={'index':index})


        links = response.xpath("//div[@class='flex-fill d-flex flex-column justify-content-end image-buttons']/a[last()-1]/@href")
        # print(links)
        for link in links:            
            yield response.follow(link.get(), callback=self.parse_item, cb_kwargs={'index':index})
                
    def parse_item(self, response, index):         
        # print("******************************")
        id = response.xpath("//section[2]/div[1]/h3/text()").get()
        lot_id = id[6:]
        # print(lot_id)
        response_url = response.url.split('/lot')      
        urls = str(response_url[0])        
        image = urls+response.css(".mediaThumbnails a img::attr(src)").get()
        # print(image) 
        description = response.css(".description-info-content p::text").get()   
        # print(description)  
        name = response.css(".lot-name::text").get()
        # print(name)        
        auctioner = response.xpath("//section[2]/div[1]/div/h3/text()[1]").get().strip()
        # print(auctioner)
        try:
            loc = auctioner.split('-')
            location = loc[1].strip()
            # print(location)
        except:
            location = "US" 
            # print(location)   
        
        try:
            auction_date = response.xpath("//span[@class='in-progress']//text()").extract()[1]   
            # print(auction_date)    
        except:
            auction_date = response.xpath("//span[@id='auc-starts-ending-date']/text()").get()
            # print(auction_date)        
    
        yield{
            'product_url' : response.url,
            'item_type' : index.strip(),
            'image_link' : image,
            'product_name': name,
            'auction_date' : auction_date,
            'location' : location,            
            'lot_id' : lot_id,
            'auctioner' : auctioner,
            'website' : "marknetalliance",
            'description' : description
        }
        


   