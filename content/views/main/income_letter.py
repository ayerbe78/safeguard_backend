from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from ..imports import *
from io import BytesIO
from django.core.files import File
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

from ..mailing.service.email_service import EmailService
from content.views.sms.views import SmsCommons
import secrets
import random
from safeguard import settings


class IncomeLetterPDFView(APIView, Common):
    def single_english(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []

        # Add client name
        current_date = datetime.now().strftime("%m/%d/%Y")
        date_paragraph = Paragraph(
            f"<para alignment='right'>{current_date}</para>", paragraph_style)
        story.append(date_paragraph)
        story.append(Spacer(5, 2/14 * inch))
        # Add client name
        client_name = f"To the Health Market:"
        client_name_paragraph = Paragraph(client_name, paragraph_style)
        story.append(client_name_paragraph)
        story.append(Spacer(5, 2/14 * inch))
        story.append(Spacer(5, 2/14 * inch))
        main_text = f"""
        I am hereby writing to you regarding the proof of income required in connection with my application number: <u><b>{context['application_id']}</b></u>.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        I declare that my address is located at: <u><b>{context['address']}</b></u>, my social security number is: <u><b>{context['ssn']}</b></u> and my date of birth is: <u><b>{context['client_dob']}</b></u>.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        I want to explain that I am currently self-employed as: <u><b>{context['working_as']}</b></u> and my annual income for 2025 will be: <u><b>${context['income']}</b></u>.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        Thank you for your prompt attention to this letter and I remain at your service for any questions or clarification.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        My personal phone number: <u><b>{context['client_tel']}</b></u>, please feel free to contact me when necessary.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        <para alignment='center'>Sincerely,</para>
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        main_text = f"""
        <para alignment='center'><u><b>{context['client_name']}</b></u></para>
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        # Add signature and date
        signature_image_data = context['signature'].read()

        # Open the image using PIL to get width and height
        with PILImage.open(BytesIO(signature_image_data)) as pil_image:
            # Resize the image to a smaller width and height
            resized_pil_image = pil_image.resize(
                (100, 100), PILImage.ANTIALIAS)
            resized_signature_image_data = BytesIO()
            resized_pil_image.save(resized_signature_image_data, format='PNG')

        # Create an Image element with the resized signature
        signature = Image(resized_signature_image_data, width=70, height=45)

        # Create a Paragraph for the date
        date_paragraph = Paragraph(
            f"Date of Signature: <font name='DancingScript' size='16'><u><b>{context['date_signature']}</b></u></font>", paragraph_style)

        signature_text = Paragraph("Signature:", paragraph_style)
        signature_table_data = [[signature_text, Spacer(0, 1), signature, Spacer(
            100, 1), date_paragraph]]
        signature_table = Table(signature_table_data, colWidths=[
                                70, None, 70, 100, 200])

        story.append(signature_table)

        return story

    def single_spanish(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        current_date = datetime.now().strftime("%m/%d/%Y")
        date_paragraph = Paragraph(
            f"<para alignment='right'>{current_date}</para>", paragraph_style)
        story.append(date_paragraph)
        story.append(Spacer(5, 2/14 * inch))
        # Add client name
        client_name = f"Al Mercado de Salud:"
        client_name_paragraph = Paragraph(client_name, paragraph_style)
        story.append(client_name_paragraph)
        story.append(Spacer(5, 2/14 * inch))
        story.append(Spacer(5, 2/14 * inch))
        main_text = f"""
        Por este medio me dirijo a ustedes con respecto a la prueba de ingresos que me requieren en relación a mi solicitud número: <u><b>{context['application_id']}</b></u>.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        Declaro que mi domicilio se ubica en: <u><b>{context['address']}</b></u>, mi número de seguro social es: <u><b>{context['ssn']}</b></u> y mi fecha de nacimiento es: <u><b>{context['client_dob']}</b></u>.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        Quiero explicarles que actualmente me encuentro trabajando por mi propia cuenta como: <u><b>{context['working_as']}</b></u> y mis ingresos anuales para el 2025 serán de <u><b>${context['income']}</b></u>.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        Les agradezco la pronta atención que brinden a la presente y quedo a sus órdenes para cualquier duda o aclaración.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        Mi número telefónico personal: <u><b>{context['client_tel']}</b></u>, por favor pueden contactarme cuando sea necesario.
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        main_text = f"""
        <para alignment='center'>Atentamente,</para>
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        main_text = f"""
        <para alignment='center'><u><b>{context['client_name']}</b></u></para>
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)
        story.append(Spacer(5, 2/14 * inch))

        signature_image_data = context['signature'].read()

        with PILImage.open(BytesIO(signature_image_data)) as pil_image:
            resized_pil_image = pil_image.resize(
                (100, 100), PILImage.ANTIALIAS)
            resized_signature_image_data = BytesIO()
            resized_pil_image.save(resized_signature_image_data, format='PNG')

        signature = Image(resized_signature_image_data, width=70, height=45)

        date_paragraph = Paragraph(
            f"Fecha de Firma: <font name='DancingScript' size='16'><u><b>{context['date_signature']}</b></u></font>", paragraph_style)

        signature_text = Paragraph("Firma:", paragraph_style)
        signature_table_data = [[signature_text, Spacer(0, 1), signature, Spacer(
            100, 1), date_paragraph]]
        signature_table = Table(signature_table_data, colWidths=[
                                50, None, 70, 100, 200])

        story.append(signature_table)
        return story

    def post(self, request, format=None):
        signature = request.data.get('signature', None)
        date_signature = request.data.get('date_signature', None)
        working_as = request.data.get('working_as', None)
        key = request.data.get('key', None)
        if not signature or not date_signature or not key:
            raise ValidationException('Missing signature')
        else:
            consent_log = IncomeLetterLog.objects.filter(secret_key=key).get()
            client = Client.objects.filter(id=consent_log.id_client)
            if consent_log.signed:
                raise ValidationException('Document already signed')
            if len(client) != 1:
                raise ValidationException('Client not found')
            else:
                client = client.get()
                dob = self.format_date(consent_log.client_dob)
                context = {
                    "signature": signature,
                    "working_as": working_as,
                    "date_signature": date_signature,
                    "client_name": consent_log.client_name,
                    "application_id": consent_log.application_id,
                    "client_id": consent_log.id_client,
                    "client_dob": dob,
                    "client_tel": consent_log.client_tel,
                    "ssn": consent_log.ssn,
                    "address": consent_log.address,
                    "income": consent_log.income if consent_log.income else '',
                }

                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                pdfmetrics.registerFont(TTFont(
                    'DancingScript', 'fonts/DancingScript/DancingScript-VariableFont_wght.ttf'))
                styles = getSampleStyleSheet()
                title_style = styles['Heading2']
                title_style.alignment = TA_CENTER
                paragraph_style = ParagraphStyle(
                    name='Normal', parent=styles['Normal'])
                paragraph_style.leading = 14  # Adjust line spacing
                paragraph_style.alignment = TA_LEFT
                bolded_style = ParagraphStyle(name='Bolded')
                bolded_style.fontName = 'Helvetica-Bold'
                bolded_style.alignment = TA_LEFT

                underlined_style = ParagraphStyle(name='Underlined')
                underlined_style.fontName = 'Helvetica'
                underlined_style.leading = 14
                underlined_style.alignment = TA_LEFT
                underlined_style.leading = 10

                if consent_log.lan == "En":
                    story = self.single_english(
                        context, title_style, paragraph_style, bolded_style, underlined_style)
                else:
                    story = self.single_spanish(
                        context, title_style, paragraph_style, bolded_style, underlined_style)

                # Add the main text

                doc.build(story)

                # Prepare the PDF file for download
                data = ClientDocument(
                    id_client=consent_log.id_client,
                    id_typedocument=11,
                    doc_name=''
                )
                data.doc_name.save(
                    f'{consent_log.client_name}_IncomeLetter.pdf', File(pdf_buffer))
                pdf_buffer.seek(0)
                consent_log.signed = True
                consent_log.date_signed = datetime.today()
                consent_log.save()
                return Response('Successfuly Submited', status=status.HTTP_200_OK)


class SendIncomeLetterSMSView(APIView, SmsCommons, Common):
    def generate_random_key(self, length):
        # // 2 to get the appropriate number of bytes
        key = secrets.token_hex(length // 2)
        return key

    def post(self, request: APIViewRequest):
        with transaction.atomic():
            service = self.sms_get_service()
            company_number = random.choice(
                self.get_company_numbers_for_mass_sending())

            id_client = request.data.get('id_client', None)
            client = Client.objects.filter(id=id_client)
            if len(client) == 1:
                client: Client = client.get()
            else:
                raise ValidationException('Bad Request')

            user = request.user
            if request.user.is_agent:
                agent = Agent.objects.filter(email=user.email)
            else:
                agent = Agent.objects.filter(id=client.id_agent)
            if len(agent) == 1:
                agent = agent.get()
                to = request.data.get('to')
                link = request.data.get('link', None)
                lan = request.data.get('lan', None)
                secret_key = self.generate_random_key(32)
                if lan == 'Es':
                    body = f"Tu agente: {agent.agent_name} {agent.agent_lastname}, le ha enviado esta Carta de Ingresos para que la firme. Puede llamar a su agente para confirmar que esto es oficial. Entre a este link para firmar la carta: {link}/sign_income_letter?key={secret_key}"
                else:
                    body = f"Your agent: {agent.agent_name} {agent.agent_lastname}, has sended you this Income Letter for you to sign. You can call your agent for confirmation that this is official. Enter to this URL to sign the Income Letter: {link}/sign_income_letter?key={secret_key}"

                message = service.send_custom_sms(
                    from_=company_number, to=to, sms=body)
            try:
                principal_income = float(client.princome)
                principal_income += float(
                    client.conincome) if client.conincome else 0
            except:
                principal_income = 0
            if message:
                data = IncomeLetterLog(
                    id_client=id_client,
                    id_agent=client.id_agent,
                    agent_name=agent.agent_name + " " + agent.agent_lastname,
                    client_name=client.names + " " + client.lastname,
                    sended=True,
                    year=date.today().year,
                    lan=lan,
                    application_id=client.application_id,
                    ssn=client.social_security,
                    address=client.addreess,
                    client_dob=client.date_birth,
                    client_tel=client.telephone,
                    income=principal_income,
                    secret_key=secret_key,
                    date_sended=datetime.today()
                )

                data.save()
                result = Response('Sended',
                                  status=status.HTTP_200_OK,
                                  )
            else:
                raise ValidationException('Not Sended')
            return result


class SendIncomeLetterEmail(APIView):
    def generate_random_key(self, length):
        # // 2 to get the appropriate number of bytes
        key = secrets.token_hex(length // 2)
        return key

    def post(self, request: APIViewRequest):
        id_client = request.data.get('id_client', None)
        client = Client.objects.filter(id=id_client)
        if len(client) == 1:
            client: Client = client.get()
        else:
            raise ValidationException('Bad Request')

        user = request.user
        if request.user.is_agent:
            agent = Agent.objects.filter(email=user.email)
        else:
            agent = Agent.objects.filter(id=client.id_agent)
        if len(agent) == 1:
            agent = agent.get()
            to = request.data.get('to')
            link = request.data.get('link', None)
            lan = request.data.get('lan', None)
            secret_key = self.generate_random_key(32)
            if lan == 'Es':
                body = f"Tu agente: {agent.agent_name} {agent.agent_lastname}, le ha enviado esta Carta de Ingresos para que la firme. Puede llamar a su agente para confirmar que esto es oficial. Entre a este link para firmar la carta: {link}/sign_income_letter?key={secret_key}"
            else:
                body = f"Your agent: {agent.agent_name} {agent.agent_lastname}, has sended you this Income Letter for you to sign. You can call your agent for confirmation that this is official. Enter to this URL to sign the Income Letter: {link}/sign_income_letter?key={secret_key}"

            service = EmailService(user_name="Health Insurance",
                                   email=settings.EMAIL_HOST_USER, passw=settings.EMAIL_SAFEGUARD_PASSWORD)
            service.send_message(to, "Income Letter", False,
                                 None, None, None, body)
            try:
                principal_income = float(client.princome)
                principal_income += float(
                    client.conincome) if client.conincome else 0
            except:
                principal_income = 0

            data = IncomeLetterLog(
                id_client=id_client,
                client_name=client.names + " " + client.lastname,
                id_agent=client.id_agent,
                agent_name=agent.agent_name + " " + agent.agent_lastname,
                sended=True,
                year=date.today().year,
                lan=lan,
                application_id=client.application_id,
                ssn=client.social_security,
                address=client.addreess,
                client_dob=client.date_birth,
                client_tel=client.telephone,
                income=principal_income,
                secret_key=secret_key,
                date_sended=datetime.today()
            )

            data.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationException('Missing data')


class GetIncomeLetterLogInformation(APIView):
    def get(self, request: HttpRequest):
        secret_key = request.GET.get('secret_key')
        try:
            client_consent_log = IncomeLetterLog.objects.filter(
                secret_key=secret_key).get()
            serializer = IncomeLetterLogSerializer(client_consent_log)
            return Response(serializer.data)
        except:
            raise ValidationException('Log not found')
