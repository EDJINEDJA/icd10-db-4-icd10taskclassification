"""

"""

#dependencies 
import requests
import csv
import os
import pandas as pd
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

    def icd92icd10(self):
        #read excel file from raw folder
        icd9icd10 = pd.read_excel(parser.get("inputPath", "path"), sheet_name=None , usecols="A:B,C")
        #Convert into dataframe
        data = pd.DataFrame(icd9icd10['masterb10 - incl 3rd vic fix'], columns=["TABLETYP", "ICD10" ,"Pure Victorian Logical"])
        #Rename columns
        data.rename(columns={"TABLETYP" : "TABLETYPE", "ICD10" : "ICD10-CM" ,"Pure Victorian Logical" : "ICD9-CM"}, inplace= True)
        print("Export progress ... ")
        #Export into csv file and save in output folder
        data.to_csv(os.path.join(parser.get("outputPath","path"),'icd9icd10.csv'))

        print("____ Export done ___")

    def merge(self):
        #Load icd92icd10 csv file located in processed folder
        correspondanceicd92icd10 = pd.read_csv(os.path.join(parser.get("outputPath","path"),'icd9icd10.csv'))
        icd10cm_order_2022 = pd.read_csv(os.path.join(parser.get("outputPath","path"),'icd10cm_order_2022.csv'))
        ICD9_CM = []
   
        for keys , values in icd10cm_order_2022["icd10code"].iteritems():
            # supposons que le dataframe s'appelle `correspondance_df`
            # et que les colonnes contenant les codes ICD-9 et ICD-10 s'appellent respectivement `icd9` et `icd10`
      
            code_icd10_recherche = values
            try: 
                valeur_icd9_correspondante = correspondanceicd92icd10.loc[correspondanceicd92icd10["ICD10-CM"] == str(code_icd10_recherche.strip()), "ICD9-CM"].iloc[0]
                ICD9_CM.append(valeur_icd9_correspondante) 
            except IndexError:
                ICD9_CM.append('No equivalence') 

        icd10cm_order_2022["icd9code"]=ICD9_CM

        #Rename columns
        icd10cm_order_2022.rename(columns={"index" : "Index","icd10code" : "ICD10-CM","keys" : "Keys","shortDescription" : "ShortDescription","description" : "Description" , "icd9code":"ICD9-CM"}, inplace= True)
        icd_final = pd.DataFrame()
        icd_final["Index"]=icd10cm_order_2022["Index"]
        icd_final["ICD10-CM"]=icd10cm_order_2022["ICD10-CM"]
        icd_final["ICD9-CM"]=icd10cm_order_2022["ICD9-CM"]
        icd_final["Keys"]=icd10cm_order_2022["Keys"]
        icd_final["ShortDescription"]=icd10cm_order_2022["ShortDescription"]
        icd_final["Description"]=icd10cm_order_2022["Description"]
        print("Export progress ... ")
        #Export into csv file and save in output folder
        icd_final.to_csv(os.path.join(parser.get("outputFinalPath","path"),'icd_final.csv'))
        print("____ Export done ___")

    def ChatGptAPi(self):
        pass 
                
        







   



    

    

    
