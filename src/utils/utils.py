"""

"""

#dependencies 
import requests
import csv
import os
from configparser import ConfigParser

parser = ConfigParser()
parser.read("./config/config.ini")


class Utils():

    def __init__(self, URL) -> None:
        self.url = URL
        self.response = requests.get(self.url)

    def __str__(self) -> str:
        return "Utils provides instance to scraped icd10 code is such a way that  for each code their descriptio. The output s in to csv file"

    def __getitem__(self):
        pass

    def __len__(self):
        pass

    def fields(self):
        # Download the text file from the URL
        text = self.response.text

        # Split the text file into lines and parse each line into fields
        lines = text.split('\n')

        for line in lines:
            #Split the text line using one blank seperator
            fields = line.split(' ')
            yield [field.strip() for field in fields if field.strip()]

    def scraper(self):
        
        rows = []
        for item in self.fields():
            if len(item)==0:
                pass
            else:
                index = item[0] #Take the first item within item
                icd10code = item[1] #Take the second item within item
                keys=item[2] #Take the third item within item
                currentWord = item[3] #keep the current word
                for idx , item_ in enumerate(item[4:]):
                    if currentWord == item_:
                       index_ = idx #keep the index of the place that it found again current word
                shortDescription = " ".join(item[3 : 3 + int(index_)+1])
                description = " ".join(item[3 + int(index_)+1 : ])
                
                rows.append([index, icd10code, keys , shortDescription , description ]) #filled in the rows 

        # Write the parsed data to a CSV file with the specified column headers
        with open(os.path.join(parser.get("outputPath","path"),'icd10cm_order_2022.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['index', 'icd10code', 'keys', 'shortDescription', 'description'])
            writer.writerows(rows)


   



    

    

    
