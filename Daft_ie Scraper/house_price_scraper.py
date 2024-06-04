from scrapy import Selector
import requests
import re


#Daft.ie
#Select County for scraping (all lowercase)
county = 'dublin'


url = 'https://www.daft.ie/property-for-sale/{}'.format(county)

#Makes it harder for websites to track you as a bot (most websites probably won't need this)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
           'Accept-Language': 'en-GB,en;q=0.5',
           'Referer': 'https://google.com',
           'DNT': '1'}

html = requests.get(url, headers=headers).content
sel = Selector(text=html)

#Find number of houses listed for search
num_of_houses_raw = sel.xpath('//h1[@data-testid="search-h1"]/text()').extract()
num_of_houses = int((num_of_houses_raw[0].split(' ')[0]).replace(',', ''))

print('Number of houses total: ', num_of_houses)


house_details = []

url_house_numbers = 0
page_number = 1
total_houses_saved = 0
still_seeing_houses = True

while still_seeing_houses == True:
    
    print('Page: ', page_number)
    page_number = page_number + 1

    html = requests.get(url, headers=headers).content
    sel = Selector(text=html)


    #This searches the html for a defined section
    raw_info = sel.xpath('//div[@data-testid="title-block"]').extract()
    
    houses_saved_per_page = 0
    for e,i in enumerate(raw_info):

        try:
            price = re.search(r'(?<=€)(.*)(?=<!)', i)[0]

            full_address = re.search(r'(?<=dzihyY">)(.*)(?=, Co.)|(?<=dzihyY">)(.*)(?=, {})'.format(county.capitalize()), i)[0]
            address = (full_address.split(', '))[-1]

            try:
                square_meter = re.search(r'(?<=floor-area" class="TitleBlock__CardInfoItem-sc-1avkvav-9 iLMdur">)(.*)(?= m²<)', i)[0]
            except:
                square_meter = 'NaN'

            if full_address not in ['63 Moylaragh Rise, Balbriggan', '208 McKee Avenue, Finglas', 'Apartment 33, The Charter, Ballymun']: #The info on daft.ie for these houses is incorrect
                
                if square_meter != 'NaN':
                    cost = float(price.replace(',', ''))
                    cost_per_area = cost/float(square_meter)
                else:
                    cost_per_area = 'NaN'
                    
                house_details.append([price, address, full_address, square_meter, cost_per_area])


            houses_saved_per_page = houses_saved_per_page + 1

        except:
            pass
        
    url_house_numbers = url_house_numbers + 20

    if url_house_numbers > num_of_houses:
        still_seeing_houses = False
    else:
        url = 'https://www.daft.ie/property-for-sale/{}/?pageSize=20&from={}'.format(county, url_house_numbers)

    total_houses_saved = total_houses_saved + houses_saved_per_page
    print('Houses Saved', houses_saved_per_page)

print('Total House Saved: ', total_houses_saved)

'''
Find relative value of house, taking into account size and location:
'''

house_details_dict = {}

for i in house_details: #[price, address, full_address, square_meter, cost_per_area]
    
    if i[3] != 'NaN':
        
        if i[1] not in house_details_dict.keys():
            house_details_dict[i[1]] = [[i[0], i[1], i[2], i[3], i[4]]]
        else:                       
            house_details_dict[i[1]].append([i[0], i[1], i[2], i[3], i[4]])


area_av_value = []

for town in house_details_dict.keys(): #Town
    value_sum = 0
    num_of_houses = 0
    for j in house_details_dict[town]: #Properties
        
        if j[3] != 'NaN':
            num_of_houses = num_of_houses + 1
            value_sum = value_sum + j[4]
    
    if num_of_houses > 2:
        av_value_sum = value_sum/num_of_houses
        area_av_value.append([town, av_value_sum, num_of_houses])
        

max_av_value = max([sublist[1] for sublist in area_av_value])

area_av_value_normalised = []
for i in area_av_value:
    normaliser = (i[1]/max_av_value)*100
    
    #print(i[0], int(i[1]), int(normaliser))
    area_av_value_normalised.append([i[0], i[1], int(i[2]), normaliser])
    
finished_list = []
for i in area_av_value_normalised:
    for e,j in enumerate(house_details_dict[i[0]]): #[price, address, full_address, square_meter, cost_per_area] + [cost_per_area_per_location]
        house_details_dict[i[0]][e].append(int(j[4]/i[3]))
        finished_list.append([j[2], j[0], j[3], int(j[4]), j[5]])
        #print(j[2], j[0], j[3], int(j[4]), j[5])
        
finished_list.sort(key=lambda x: x[4])

'''
Select min/max price range to return properites in that range. Results are ordered in terms of best relative value 
(Denoted by a number between 0 - 100, with the lower the number, the better the value)
'''

min_cost = 0
max_cost = 300000
min_size = 80

print('Address    |    Price    |    Floor Area    |    Price per Square Meter    |    Relative Value')

for i in finished_list:
    if float((i[1]).replace(',', '')) > min_cost and float((i[1]).replace(',', '')) < max_cost and int(i[2]) > min_size:
        print(i)
        
