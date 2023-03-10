"""

"""

#dependencies 
import requests
import csv
import os
import pandas as pd
import openai
import pprint
from  tqdm import tqdm
from configparser import ConfigParser
import json
import time

parser = ConfigParser()
parser.read("./config/config.ini")

with open("./secret/secret.json") as f:
    api_key = json.load(f)


class Utils():

    def __init__(self) -> None:
        pass
        

    def __str__(self) -> str:
        return "Utils provides instance to scraped icd10 code is such a way that  for each code their descriptio. The output s in to csv file"

    def __getitem__(self):
        pass

    def __len__(self):
        pass

    def fields(self):
        URL = 'https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2022/icd10cm_order_2022.txt'
        self.url = URL
        response = requests.get(self.url)
        # Download the text file from the URL
        text = response.text

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

    @staticmethod
    # Define function to generate response
    def generate_response(prompt, model , temperature):
        response = openai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature = temperature
        )

        return response
        
    def ChatGptAPi(self , content , temperature = 0):
        # Set OpenAI API key
        openai.api_key = api_key["api-keys"]
   
        # Set up the OpenAI model
        model_engine = "gpt-3.5-turbo"
        model_prompt = [{"role" : "system" ,"content" : f"{content}"
                        }] # Change the question prompt as needed
  
        # Generate response using the defined function
        response = self.generate_response(model_prompt, model_engine, temperature)

        # return the response
        return response['choices'][0]['message']['content']

    def Q2text(self):

        #Load icd_final.csv
        icd_final = pd.read_csv(parser.get("outputFinalPath" , "load"))

        if not os.path.exists(parser.get("outputFinalPath","inProgressFile")):
            with open(parser.get("outputFinalPath","inProgressFile"), "w", newline="") as file:
                file.close()
        
        if not os.path.exists(os.path.join(parser.get("outputFinalPath" , "path"),"log.json")):
            with open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), 'w') as f:
                json.dump({},f)
                # définir la taille du fichier à 0 octet
            os.truncate(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), 0)
  
        if os.path.getsize(parser.get("outputFinalPath","inProgressFile")) == 0:
            # Ouverture du fichier en mode 'append' pour ajouter de nouvelles lignes
            with open(os.path.join(parser.get("outputFinalPath","path"),'icd_datasets.csv'), mode='a', newline='') as file:
                # Définition des colonnes dans un objet DictWriter
                writer = csv.DictWriter(file, fieldnames=["Index", "ICD10-CM" , "ICD9-CM", "Keys", "ShortDescription", "Description", "Text"])

                # Écriture de l'en-tête
                writer.writeheader()

        else : 
 
            if os.path.getsize(os.path.join(parser.get("outputFinalPath" , "path"),"log.json")) == 0:
                with open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), mode='w') as f:
                    keys = "1"
                    icd10 = "A00"
                    data = {f"{keys}" : f"{icd10}"}
                    # Écrire l'objet JSON dans le fichier
                    json.dump(data, f)
                    
                    # Ajouter un retour à la ligne pour séparer les objets JSON
                    f.write("\n")
                    f.close()
            else:
                data = [json.loads(line) for line in open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json") , mode ="r")]  
                cursor = data[-1].values()
                valeurs = list(cursor) # conversion de la vue en liste
                valeur = valeurs[0] # accès à la première valeur de la liste
                # Trouver l'index de l'élément "valeur" dans la colonne "colonne"
                index = icd_final["ICD10-CM"].index[icd_final["ICD10-CM"] == valeur][0]

                for keys_ , icd10_ in tqdm(icd_final["ICD10-CM"].iloc[index:].iteritems()):

                    compt = 0
                    des = icd_final.loc[icd_final["ICD10-CM"] == icd10_, "ShortDescription"].iloc[0]+ "," + icd_final.loc[icd_final["ICD10-CM"] == icd10_, "Description"].iloc[0]
                    prompt = f"ICD10-CM = {icd10_} which has in the context of the international classification of disease codes the description:{des}. Give me a text of a patient who expresses his symptoms that he has related to this type of disease to his doctor in form discussion with his doctor."
                    
                    with open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), mode='w') as f:
                        data = {f"{keys_}" : f"{icd10_}"}
                        # Écrire l'objet JSON dans le fichier
                        json.dump(data, f)
                        
                        # Ajouter un retour à la ligne pour séparer les objets JSON
                        f.write("\n")
                        f.close()
                    
                    while compt !=5:
                        text = self.ChatGptAPi(prompt)

                        
                        row =[icd_final.loc[icd_final["ICD10-CM"] == icd10_, "Index"].iloc[0],icd10_,icd_final.loc[icd_final["ICD10-CM"] == icd10_, "ICD9-CM"].iloc[0]
                        ,icd_final.loc[icd_final["ICD10-CM"] == icd10_, "Keys"].iloc[0],icd_final.loc[icd_final["ICD10-CM"] == icd10_, "ShortDescription"].iloc[0],
                       icd_final.loc[icd_final["ICD10-CM"] == icd10_, "Description"].iloc[0], text ]
                       
                        # Ouverture du fichier en mode 'append' pour ajouter de nouvelles lignes
                        with open(os.path.join(parser.get("outputFinalPath","path"),'icd_datasets.csv'), mode='a', newline='') as file1:
                            writer1 = csv.writer(file1)
                            # Écriture d'une nouvelle ligne dans le fichier CSV
                            writer1.writerow(row)

                        compt = compt + 1
                        time.sleep(60)
                        
    def Q2textBeta(self):

        #Load icd_final.csv
        icd_final = pd.read_csv(parser.get("outputFinalPath" , "load"))
        # Ouverture du fichier en mode 'append' pour ajouter de nouvelles lignes
        with open(os.path.join(parser.get("outputFinalPath","path"),'icd_datasets.csv'), mode='a', newline='') as file:
            #writer = csv.writer(file)
            # Définition des colonnes dans un objet DictWriter
            writer = csv.DictWriter(file, fieldnames=["Index", "ICD10-CM" , "ICD9-CM", "Keys", "ShortDescription", "Description", "Text"])

            # Écriture de l'en-tête
            writer.writeheader()
            

            for keys , icd10 in tqdm(icd_final["ICD10-CM"].iteritems()):
                compt = 0
                des = icd_final.loc[icd_final["ICD10-CM"] == icd10, "ShortDescription"].iloc[0]+ "," + icd_final.loc[icd_final["ICD10-CM"] == icd10, "Description"].iloc[0]
                prompt = f"ICD10-CM = {icd10} which has in the context of the international classification of disease codes the description:{des}. Give me a text of a patient who expresses his symptoms that he has related to this type of disease to his doctor in form discussion with his doctor."
                while compt !=5:
                    text = self.ChatGptAPi(prompt)

                    row = {"Index" : icd_final.loc[icd_final["ICD10-CM"] == icd10, "Index"].iloc[0],
                    "ICD10-CM" : icd10,
                    "ICD9-CM" : icd_final.loc[icd_final["ICD10-CM"] == icd10, "ICD9-CM"].iloc[0],
                    "Keys" : icd_final.loc[icd_final["ICD10-CM"] == icd10, "Keys"].iloc[0], 
                    "ShortDescription" : icd_final.loc[icd_final["ICD10-CM"] == icd10, "ShortDescription"].iloc[0],
                    "Description" : icd_final.loc[icd_final["ICD10-CM"] == icd10, "Description"].iloc[0],
                    "Text" : text}

                    # Écriture d'une nouvelle ligne dans le fichier CSV
                    writer.writerow(row)

                    compt = compt + 1







   



    

    

    
