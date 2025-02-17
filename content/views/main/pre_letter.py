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


class PreLetterPDFView(APIView, Common):
    def single_english(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        title = Paragraph("CLIENT CONSENT FORM", title_style)
        story.append(title)
        story.append(Spacer(5, 2/14 * inch))

        # Add client name

        client_name_paragraph = [
            [

                Paragraph(
                    f"I, <u><b>{context['client_name']}</b></u>", paragraph_style),
                Paragraph(
                    f"DOB:<u><b>{context['client_dob']}</b></u>", paragraph_style),
            ]

        ]
        client_name_table = Table(client_name_paragraph, colWidths=[
            3.5 * inch, 3 * inch])
        client_name_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(client_name_table)

        main_text = """
        am requesting assistance in receiving a QUOTE through the Health Insurance Marketplace for reduced premium benefits. I hereby give permission to:
        """
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)

        # Add the agent information
        agent_info = [
            [Paragraph(f"Authorized Agent: <u><b>{context['main_agent_name']}</b></u>", underlined_style),
                Paragraph(
                f"NPN: <u><b>{context['main_agent_npn']}</b></u>", underlined_style),
                Paragraph(f"Telephone: <u><b>{context['main_agent_tel']}</b></u>", underlined_style)]
        ]
        agent_table = Table(agent_info, colWidths=[
                            3.5 * inch, 1.2 * inch, 1.3 * inch])
        agent_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(agent_table)

        # Add more text
        story.append(Spacer(5, 2/14 * inch))
        more_text = f"to act as my family's Health Insurance Agent. By consenting to this agreement, I authorize the use of confidential information provided in writing, electronically or by telephone."
        more_text_paragraph = Paragraph(more_text, paragraph_style)
        story.append(more_text_paragraph)

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
            f"Date of Signature: <font name='DancingScript' size='12'><u><b>{context['date_signature']}</b></u></font>", paragraph_style)

        signature_text = Paragraph("Signature:", paragraph_style)
        signature_table_data = [[signature_text, Spacer(0, 1), signature, Spacer(
            100, 1), date_paragraph]]
        signature_table = Table(signature_table_data, colWidths=[
                                70, None, 70, 100, 200])

        story.append(signature_table)

        return story

    def single_spanish(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        title = Paragraph("CARTA DE CONSENTIMIENTO", title_style)
        story.append(title)
        story.append(Spacer(5, 2/14 * inch))

        # Add client name

        client_name_paragraph = [
            [

                Paragraph(
                    f"Yo, <u><b>{context['client_name']}</b></u>", paragraph_style),
                Paragraph(
                    f"DOB:<u><b>{context['client_dob']}</b></u>", paragraph_style),
            ]

        ]
        client_name_table = Table(client_name_paragraph, colWidths=[
            3.5 * inch, 3 * inch])
        client_name_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(client_name_table)
        main_text = f"estoy solicitando asistencia para recibir una COTIZACIÓN por Medio del Mercado de Seguros Médicos y así obtener beneficios de una prima reducida. Por este medio doy permiso a:"
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)

        # Add the agent information
        agent_info = [
            [Paragraph(f"Agente Autorizado: <u><b>{context['main_agent_name']}</b></u>", underlined_style),
                Paragraph(
                f"NPN: <u><b>{context['main_agent_npn']}</b></u>", underlined_style),
                Paragraph(f"Teléfono: <u><b>{context['main_agent_tel']}</b></u>", underlined_style)]
        ]
        agent_table = Table(agent_info, colWidths=[
                            3.5 * inch, 1.2 * inch, 1.3 * inch])
        agent_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(agent_table)

        # Add more text
        story.append(Spacer(5, 2/14 * inch))
        more_text = f"para actuar como mi Agente de Seguro de Salud de mi familia. Al dar mi consentimiento a este acuerdo, autorizo a utilizar la información confidencial proporcionada por escrito, electrónicamente o por teléfono."
        more_text_paragraph = Paragraph(more_text, paragraph_style)
        story.append(more_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))

        signature_image_data = context['signature'].read()

        with PILImage.open(BytesIO(signature_image_data)) as pil_image:
            resized_pil_image = pil_image.resize(
                (100, 100), PILImage.ANTIALIAS)
            resized_signature_image_data = BytesIO()
            resized_pil_image.save(resized_signature_image_data, format='PNG')

        signature = Image(resized_signature_image_data, width=70, height=45)

        date_paragraph = Paragraph(
            f"Fecha de Firma: <font name='DancingScript' size='12'><u><b>{context['date_signature']}</b></u></font>", paragraph_style)

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
        key = request.data.get('key', None)
        if not signature or not date_signature or not key:
            raise ValidationException('Missing signature')
        else:
            consent_log = PreLetterLog.objects.filter(secret_key=key).get()
            if consent_log.signed:
                raise ValidationException('Document already signed')
            else:
                dob = self.format_date(consent_log.client_dob)
                context = {
                    "signature": signature,
                    "date_signature": date_signature,
                    "client_name": consent_log.client_name,
                    "client_dob": dob,
                    "main_agent_name": consent_log.agent_name,
                    "main_agent_npn": consent_log.agent_npn,
                    "main_agent_tel": consent_log.agent_phone,
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

                consent_log.file.save(
                    f'{consent_log.client_name}_Pre_Letter.pdf', File(pdf_buffer))
                pdf_buffer.seek(0)
                consent_log.signed = True
                consent_log.date_signed = datetime.today()
                consent_log.save()
                return Response('Successfuly Submited', status=status.HTTP_200_OK)


class GetPreLetterInformation(APIView):
    def get(self, request: HttpRequest):
        secret_key = request.GET.get('secret_key')
        try:
            client_consent_log = PreLetterLog.objects.filter(
                secret_key=secret_key).get()
            serializer = PreLetterLogSerializer(client_consent_log)
            return Response(serializer.data)
        except:
            raise ValidationException('Log not found')


class SendPreLetterEmail(APIView):
    def generate_random_key(self, length):
        # // 2 to get the appropriate number of bytes
        key = secrets.token_hex(length // 2)
        return key

    def post(self, request: APIViewRequest):
        user = request.user
        if request.user.is_agent:
            agent = Agent.objects.filter(email=user.email)
        else:
            agent = Agent.objects.filter(id=request.data.get('agent'))
        if len(agent) == 1:
            agent = agent.get()
            to = request.data.get('to')
            link = request.data.get('link', None)
            lan = request.data.get('lan', None)
            client_name = request.data.get('client_name', None)
            client_dob = request.data.get('client_dob', None)
            client_tel = request.data.get('client_tel', None)
            client_email = request.data.get('client_email', None)
            secret_key = self.generate_random_key(32)
            if lan == 'Es':
                body = f"Tu agente: {agent.agent_name} {agent.agent_lastname}, le ha enviado este Acuerdo de Consentimiento para que lo firme. Puede llamar a su agente para confirmar que esto es oficial. Entre a este link para firmar el Consentimiento: {link}/sign_pre_letter?key={secret_key}"
            else:
                body = f"Your agent: {agent.agent_name} {agent.agent_lastname}, has sended you this Client Consent for you to sign. You can call your agent for confirmation that this is official. Enter to this URL to sign the Client Consent: {link}/sign_pre_letter?key={secret_key}"

            service = EmailService(user_name="Health Insurance",
                                   email=settings.EMAIL_HOST_USER, passw=settings.EMAIL_SAFEGUARD_PASSWORD)
            service.send_message(to, "Client Consent", False,
                                 None, None, None, body)
            data = PreLetterLog(
                id_agent=agent.id,
                agent_name=agent.agent_name + " " + agent.agent_lastname,
                sended=True,
                year=date.today().year,
                lan=lan,
                agent_npn=agent.npn,
                agent_phone=agent.telephone,
                client_name=client_name,
                client_dob=client_dob,
                client_tel=client_tel,
                client_email=client_email,
                secret_key=secret_key,
                date_sended=datetime.today()
            )

            data.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationException('Missing data')


class SendPreLetterSMSView(APIView, SmsCommons, Common):
    def generate_random_key(self, length):
        # // 2 to get the appropriate number of bytes
        key = secrets.token_hex(length // 2)
        return key

    def post(self, request: APIViewRequest):
        with transaction.atomic():
            service = self.sms_get_service()
            company_number = random.choice(
                self.get_company_numbers_for_mass_sending())

            user = request.user
            if request.user.is_agent:
                agent = Agent.objects.filter(email=user.email)
            else:
                agent = Agent.objects.filter(id=request.data.get('agent'))
            if len(agent) == 1:
                agent = agent.get()
                to = request.data.get('to')
                link = request.data.get('link', None)
                lan = request.data.get('lan', None)
                client_name = request.data.get('client_name', None)
                client_dob = request.data.get('client_dob', None)
                client_tel = request.data.get('client_tel', None)
                client_email = request.data.get('client_email', None)
                secret_key = self.generate_random_key(32)
                if lan == 'Es':
                    body = f"Tu agente: {agent.agent_name} {agent.agent_lastname}, le ha enviado este Acuerdo de Consentimiento para que lo firme. Puede llamar a su agente para confirmar que esto es oficial. Entre a este link para firmar el Consentimiento: {link}/sign_pre_letter?key={secret_key}"
                else:
                    body = f"Your agent: {agent.agent_name} {agent.agent_lastname}, has sended you this Client Consent for you to sign. You can call your agent for confirmation that this is official. Enter to this URL to sign the Client Consent: {link}/sign_pre_letter?key={secret_key}"

                message = service.send_custom_sms(
                    from_=company_number, to=to, sms=body)

            if message:
                data = PreLetterLog(
                    id_agent=agent.id,
                    agent_name=agent.agent_name + " " + agent.agent_lastname,
                    sended=True,
                    year=date.today().year,
                    lan=lan,
                    agent_npn=agent.npn,
                    agent_phone=agent.telephone,
                    client_name=client_name,
                    client_dob=client_dob,
                    client_tel=client_tel,
                    client_email=client_email,
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


class DataForPreLetterLog(APIView, AgencyManagement):
    permission_classes = [HasPreLetterLogPermission]

    def get(self, request: HttpRequest):
        user: CustomUser = request.user
        return Response(self.get_selects(user.pk, "agents"))


class TransferPreLetterToClient(APIView, AgencyManagement):
    permission_classes = [HasPreLetterLogPermission]

    def post(self, request: HttpRequest):
        client = request.data.get('client')
        id_log = request.data.get('id')
        clients = self.get_related_clients(
            request.user.pk, True).filter(id=client)
        agents = self.get_related_agents(
            request.user.pk, include_self=True, only=['id'])
        log = PreLetterLog.objects.filter(id=id_log, id_agent__in=agents)
        if clients.exists() and log.exists():
            client = clients.get()
            log = log.get()
        else:
            raise ValidationException("Wrong Data")
        with transaction.atomic():
            data = ClientDocument(
                id_client=client.pk,
                id_typedocument=12,
                doc_name=log.file
            )
            data.save()

            log.delete()

            return Response(status.HTTP_201_CREATED)


class TransferPreLetterToApplication(APIView, AgencyManagement):
    permission_classes = [HasPreLetterLogPermission]

    def post(self, request: HttpRequest):
        application = request.data.get('application')
        id_log = request.data.get('id')
        applications = self.get_related_applications(
            request.user.pk, True).filter(id=application)
        agents = self.get_related_agents(
            request.user.pk, include_self=True, only=['id'])
        log = PreLetterLog.objects.filter(id=id_log, id_agent__in=agents)
        if applications.exists() and log.exists():
            application = applications.get()
            log = log.get()
        else:
            raise ValidationException("Wrong Data")
        with transaction.atomic():
            data = ClientDocument(
                id_client=application.pk,
                id_typedocument=12,
                doc_name=log.file
            )
            data.save()

            log.delete()

            return Response(status.HTTP_201_CREATED)
