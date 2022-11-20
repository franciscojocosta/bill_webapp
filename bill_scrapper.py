
from asyncio.windows_events import NULL
from pickle import TRUE
import PyPDF2

import os
import django
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.WARNING)


record = (0,0) ## Variable to store bill data
src_path = 'C:\\Users\\franc\\Downloads'  #### Path to check for bills

class MonitorFolder(FileSystemEventHandler):
    ## When downloading bills, observer gets multiple entrys of filename, filename_aux variable validates if filename already processed.
    filename_aux = ""

    def edpmatch(self,filename):
        ### EDP bill names has 12 integers at the beggining
        if len(filename) < 12:  
            return False

        for i in range(12):
            if filename[i].isnumeric() == False: 
                break
            
            if i == 11 and self.filename_aux != filename:  
                
                if len(filename) < 22 and ".pdf" in filename: 
                    self.filename_aux = filename
                    return True
               
    def aguamatch(self,filename):
        
        if "985.AR.DP." in filename and filename != self.filename_aux:
            self.filename_aux = filename
            return TRUE

    def get_agua(self, filename,filepath): 
        logging.info('Bill: %s is being processed', filename)
        bill_handler('agua',filepath)

    def get_edp(self, filename,filepath): 
        logging.info('Bill: %s is being processed', filename)
        bill_handler('EDP',filepath)

    def on_modified(self, event):

        filepath = event.src_path
        filename = os.path.basename(filepath)

        if self.aguamatch(filename): self.get_agua(filename, filepath)

        elif self.edpmatch(filename): self.get_edp(filename, filepath)

        else: pass

class bill_handler():
    def edp_bill_month(self,per):
        convert ={"janeiro":"01","fevereiro":"02","março":"03","abril":"04","maio":"05","junho":"06","julho":"07","agosto":"08","setembro":"09","outubro":"10","novembro":"11","dezembro":"12"}
        per = per.replace("a ","")

        for key in convert:
                if key in per:
                    val =(convert.get(key))
                    per = per.replace(key,val)

        nd = per[11:]
        month = nd[3:5] + "/" + nd[-2:] 

        return month

    def agua_bill_month(self,per):
        per = per.replace("~ ","")
        nd = per[11:]
        month = nd[5:7] + "/" + nd[2:4] 

        return month 

    def edp(self,filepath):

        filename = os.path.basename(filepath) # Get filename from filepath

        try:
            pdfFileObj = open(filepath, 'rb')
        except OSError:
            logging.error('Cannot open bill file')
            sys.exit()

        with pdfFileObj:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            text=''
            pageObj = pdfReader.getPage(pdfReader.numPages - 1) ## Get only last Page. Where Bills info is at.
            text=text+pageObj.extractText()

        #Periodo de facturação

        per_find ='Período de faturação: '
        per_find_ix = text.find(per_find)
        per_find_size = len(per_find)
        per_ix = per_find_ix + per_find_size
        per_y1_ix = text[per_ix:].find('202')
        per_y2_ix = text[per_ix + per_y1_ix +1 :].find('202')
        per_size = per_y1_ix + per_y2_ix + 5
        per = text[per_ix : per_ix + per_size]
        per = self.edp_bill_month(per)

        #Entidade

        ent_find = 'Data limite de pagamento: '
        ent_find_ix = text.find(ent_find) ## tem 24 caracteres
        ent_find_size = len(ent_find)
        ent_ix = ent_find_ix + ent_find_size
        ent_size = 5
        ent = text[ent_ix : ent_ix + ent_size]

        # Referência

        ref_ix = ent_ix + ent_size + 2
        ref_size = 11
        ref = text[ref_ix : ref_ix + ref_size].replace(" ","")

        # Valor a Pagar

        price_ix = ref_ix + ref_size + 2
        euro_ix = text[price_ix:].find('€')
        price_size = euro_ix - 1
        price = text[price_ix : price_ix + price_size].replace(",",".")

        # Data Limite

        lim_date_ix = price_ix + euro_ix + 2
        lim_date_size = 10
        lim_date = text[lim_date_ix : lim_date_ix + lim_date_size]
        lim_date = lim_date[6:] + "-" + lim_date[3:5] + "-" + lim_date[:2]

        ### Gather all information

        try:
            bills = ('EDP',filename[0:12], float(price), str(per), int(ent), int(ref), lim_date)
        except:
            bills = NULL
        return bills

    def agua(self,filepath): 
        
        filename = os.path.basename(filepath)

        try:
            pdfFileObj = open(filepath, 'rb')
        except OSError:
            logging.error('Cannot open bill file')
            sys.exit()
        with pdfFileObj:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            text=''
            pageObj = pdfReader.getPage(0) ## Get only first Page. Where Bills info is at.
            text=text+pageObj.extractText()
        
        #Periodo de facturação

        per_find ='Resumo de faturação Período Faturação: '
        per_find_ix = text.find(per_find)
        per_find_size = len(per_find)
        per_ix = per_find_ix + per_find_size
        per_size = 23
        per = text[per_ix : per_ix + per_size]
        per = self.agua_bill_month(per)
        
        #Entidade

        ent_find = 'do Credor (IDC) PT20110442.'
        ent_find_ix = text.find(ent_find) ## tem 24 caracteres
        ent_find_size = len(ent_find)
        ent_ix = ent_find_ix + ent_find_size + 1
        ent_size = 5
        ent = text[ent_ix : ent_ix + ent_size]
        
        # Valor a Pagar

        price_ix = ent_ix + ent_size + 1
        euro_ix = text[price_ix:].find('€')
        price_size = euro_ix
        price = text[price_ix : price_ix + price_size].replace(",",".")
        
        # Referência

        ref_ix = price_ix + price_size + 1
        ref_size = 11
        ref = text[ref_ix : ref_ix + ref_size].replace(" ","")

        # Data Limite

        lim_dat_find = 'Data limite pagamento'
        lim_dat_find_ix = text.find(lim_dat_find) ## tem 24 caracteres
        lim_dat_find_size = len(lim_dat_find)
        
        lim_dat_ix = lim_dat_find_ix + lim_dat_find_size + 1
        lim_dat_size = 11
        lim_date = text[lim_dat_ix : lim_dat_ix + lim_dat_size].replace(" ","-")
        convert ={"jan":"01","feb":"02","mar":"03","abr":"04","mai":"05","jun":"06","jul":"07","ago":"08","set":"09","out":"10","nov":"11","dec":"12"}
        
        for key in convert:
            if key in lim_date:
                val =(convert.get(key))
                break
            else:
                val = "00"

        lim_date = lim_date.replace(key,val)
        lim_date = lim_date[6:] + "-" + lim_date[3:5] + "-" + lim_date[:2]
        
        ### Gather all information
        try: 
            bills = ('Agua',filename[0:19], float(price), per, int(ent), int(ref), lim_date)
        except:
            bills = NULL

        return bills

    def store_bill(self,tipo,filepath):
        ### DB connection
        
        try:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bill_webapp.settings")
            django.setup()
            from bill_data.models import bill_data

        except :
            logging.error('Cant setup djanfo env')
            

        if tipo == 'EDP':
            record = self.edp(filepath)
        elif tipo == 'agua':
            record = self.agua(filepath)
        else: record = NULL

        if record == NULL:
            logging.error('Error populating record variable')
            pass

        else:

            if bill_data.objects.filter(bill_id=record[1]).exists(): ## Check if bill_id already exists
                fatura_entrys = 1
            else: fatura_entrys = 0  
            
            if fatura_entrys < 1: ## store bill 
                try:
                    bill = bill_data(bill_type=record[0], bill_id = record[1], price = record[2], bill_period = record[3], entity = record[4], reference = record[5], limit_date = record[6])
                    bill.save()
                except:
                    logging.error('Error on fatura query')
                    pass
                logging.info('Bill stored %s', record)

            else:
                logging.warning('Already a bill with this id.')

           

    def __init__(self, tipo, filepath):
        
        self.store_bill(tipo,filepath)

if __name__ == "__main__":
    
    event_handler=MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    
    logging.info('Monitoring Started')
    
    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()


