from src.utils import utils

parser = utils.Utils('https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2022/icd10cm_order_2022.txt')
parser.merge()