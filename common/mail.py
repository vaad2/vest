from django.conf import settings
from django.template.loader import render_to_string
def mail_template_send(cls, name, context = {}, skip_site_checking = False):

    from django.core.mail import send_mail, EmailMultiAlternatives
    from django.template import Context, Template
    if not 'from_email' in context:
        try:
            context['from_email'] = settings.DEFAULT_FROM_EMAIL
        except BaseException, e:
            pass

    c = Context(context)

    if hasattr(cls, 'site_objects') and not skip_site_checking:
        qset = cls.site_objects.filter(state = 1, name = name)
    else:
        qset = cls.objects.filter(state = 1, name = name)

    for tpl in qset:
        rcps = Template(tpl.recipients).render(c).split(',')

        if hasattr(tpl, 'text_content'):
            #process old version
            text = Template(tpl.text_content).render(c)
            html = Template(tpl.html_content).render(c)

        else:
            #process site template based version
            text = render_to_string(tpl.template_text.name, context) if tpl.template_text else ''
            html = render_to_string(tpl.template_html.name, context) if tpl.template_html else ''



        subject = Template(tpl.subject).render(c)
        from_email = Template(tpl.from_email).render(c)

        msg = EmailMultiAlternatives(subject, text, from_email, rcps)
        msg.attach_alternative(html, "text/html")
        msg.send()
