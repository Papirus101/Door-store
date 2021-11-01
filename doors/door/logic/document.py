from django.core.mail import EmailMessage
from docxtpl import DocxTemplate


class SendCheckOrder:

    @staticmethod
    def genereta_check(form, order):
        """ Генерирует документ для отправки """
        doc = DocxTemplate("check.docx")
        context = {'checnum': form.cleaned_data['num_check'],
                   'day': form.cleaned_data['day'],
                   'month': form.cleaned_data['month'],
                   'year': form.cleaned_data['year'],
                   'companyname': order.company_name,
                   'inn': form.cleaned_data['inn'],
                   'kpp': form.cleaned_data['kpp'],
                   'index': form.cleaned_data['index'],
                   'address': form.cleaned_data['address'],
                   'door': order.door.name,
                   'doorcount': order.count_doors,
                   'doorprice': order.door.price + order.door.personal_margin,
                   'sum': (order.door.price + order.door.personal_margin) * order.count_doors}
        doc.render(context)
        doc.save("media/check_gen.docx")

    @staticmethod
    def send_mail_check(mail_to):
        """ Отправка письма с счётом на оплату """
        email = EmailMessage(subject='Счёт на оплату', body='Текст письма', to=mail_to)
        email.attach_file('media/check_gen.docx')
        email.send()
