import os
import django

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bill_webapp.settings")
    django.setup()

    # now you have access to your models
    # as an example:

    from bill_data.models import bill_data
    # 
    tlisp = bill_data(bill_type='edp', bill_id = 'fsfs23', price = 23, bill_period = "Janeiro", entity = "123123", reference = "4234435", limit_date = "2022-05-23")
    tlisp.save()
    records = bill_data.objects.values_list('bill_id')
    print (records)
    if bill_data.objects.filter(bill_id='985.AR.DP.14328123').exists(): print('Já está')
    