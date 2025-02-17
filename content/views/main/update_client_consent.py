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


class UpdateClientAgreementPDFView(APIView, Common):
    def single_english(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        title = Paragraph("CLIENT UPDATE CONSENT FORM", title_style)
        story.append(title)

        # Add client name
        client_name = f"I, <u><b>{context['client_name']}</b></u>"
        client_name_paragraph = Paragraph(client_name, paragraph_style)
        story.append(client_name_paragraph)

        main_text = """
        am requesting the assistance of my agent <u><b>{}, NPN {}</b></u>, authorizing him/her to make the following change(changes) to my policy <u><b>{}</b></u>, using the information I have provided.
        """.format(context['main_agent_name'], context['main_agent_npn'], context['update_type'])
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))
        more_text_paragraph = Paragraph("Plan Details", paragraph_style)
        story.append(more_text_paragraph)

        list_items = [
            f"Plan Name: {context['client_plan_name']}",
            f"Monthly Payment: {context['client_monthly_payment']}",
            f"Deductible: {context['client_deductible']}",
            f"Max Out of Pocket: {context['client_max_out_pocket']}",
            f"Total Income: {context['client_principal_income']}",
            f"Effective Date: {context['client_effective_date']}",
        ]

        list_item_style = ParagraphStyle(
            name='ListItemStyle',
            parent=paragraph_style,
            leftIndent=10,
            spaceBefore=0,
            spaceAfter=1,
            bulletFontName='Helvetica',
        )
        for item in list_items:
            # Add whatever prefix you need
            paragraph = Paragraph(f"- {item}", list_item_style)
            story.append(paragraph)

        story.append(Spacer(5, 2/14 * inch))

        more_text = """
        I understand that my consent remains in effect until it is revoked or modified by contacting the agent named above, and that my personal information will not be disclosed and will be stored securely.

        I also understand that in cases of changes such as:
        """.format(context['main_agent_name'])
        more_text_paragraph = Paragraph(more_text, paragraph_style)
        story.append(more_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))

        # Add a bullet list
        bullet_points = [
            "Marital status.",
            "Income amount/type.",
            "The number of people on my tax return.",
            "The number of people who need health coverage on my application.",
            "Immigration status.",
            "Home address."
        ]

        bullet_list = ListFlowable(
            [ListItem(Paragraph(point))
                for point in bullet_points],
            bulletType='bullet',
            leftIndent=20,  # Adjust the left indentation
            spaceAfter=5,
        )
        story.append(bullet_list)

        # Add more text
        more_text2 = """
        I must notify my representative so that they may update my information.

        I also confirm not to have any other active health insurance plan.
        """
        more_text_paragraph2 = Paragraph(more_text2, paragraph_style)
        story.append(more_text_paragraph2)

        story.append(Spacer(5, 2/14 * inch))

        # Add signature and date
        signature_info1 = [
            [Paragraph(f"Date of Birth: <u><b>{context['client_dob']}</b></u>", underlined_style),
                Paragraph(
                f"Telephone: <u><b>{context['client_tel']}</b></u>", underlined_style),
                Paragraph(f"Email: <u><b>{context['client_email']}</b></u>", underlined_style)]
        ]
        signature_table1 = Table(signature_info1, colWidths=[
            1.8 * inch, 1.8 * inch, 2.5 * inch])
        signature_table1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(signature_table1)

        story.append(Spacer(5, 2/14 * inch))
        # Add more text
        more_text3 = """
        By typing your name in this space, you legally represent your real signature and acknowledge that the information provided is accurate and valid to the best of your knowledge.
        """
        more_text_paragraph3 = Paragraph(more_text3, paragraph_style)
        story.append(more_text_paragraph3)

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

    def double_english(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        title = Paragraph("CLIENT UPDATE CONSENT FORM", title_style)
        story.append(title)

        # Add client name
        client_name = f"I, <u><b>{context['client_name']}</b></u>"
        client_name_paragraph = Paragraph(client_name, paragraph_style)
        story.append(client_name_paragraph)
        main_text = """
        am requesting the assistance of my agents <u><b>{}, NPN {} and {}, NPN {}</b></u>, authorizing them to make the following change(changes) to my policy <u><b>{}</b></u>, using the information I have provided.
        """.format(context['main_agent_name'], context['main_agent_npn'], context['secondary_agent_name'], context['secondary_agent_npn'], context['update_type'])
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))
        more_text_paragraph = Paragraph("Plan Details", paragraph_style)
        story.append(more_text_paragraph)

        list_items = [
            f"Plan Name: {context['client_plan_name']}",
            f"Monthly Payment: {context['client_monthly_payment']}",
            f"Deductible: {context['client_deductible']}",
            f"Max Out of Pocket: {context['client_max_out_pocket']}",
            f"Total Income: {context['client_principal_income']}",
            f"Effective Date: {context['client_effective_date']}",
        ]

        list_item_style = ParagraphStyle(
            name='ListItemStyle',
            parent=paragraph_style,
            leftIndent=10,
            spaceBefore=0,
            spaceAfter=1,
            bulletFontName='Helvetica',
        )
        for item in list_items:
            # Add whatever prefix you need
            paragraph = Paragraph(f"- {item}", list_item_style)
            story.append(paragraph)

        story.append(Spacer(5, 2/14 * inch))

        more_text = """
        I understand that my consent remains in effect until it is revoked or modified by contacting the agent named above, and that my personal information will not be disclosed and will be stored securely.

        I also understand that in cases of changes such as:
        """.format(context['main_agent_name'])
        more_text_paragraph = Paragraph(more_text, paragraph_style)
        story.append(more_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))

        # Add a bullet list
        bullet_points = [
            "Marital status.",
            "Income amount/type.",
            "The number of people on my tax return.",
            "The number of people who need health coverage on my application.",
            "Immigration status.",
            "Home address."
        ]

        bullet_list = ListFlowable(
            [ListItem(Paragraph(point))
                for point in bullet_points],
            bulletType='bullet',
            leftIndent=20,  # Adjust the left indentation
            spaceAfter=5,
        )
        story.append(bullet_list)

        # Add more text
        more_text2 = """
        I must notify my representative so that they may update my information.

        I also confirm not to have any other active health insurance plan.
        """
        more_text_paragraph2 = Paragraph(more_text2, paragraph_style)
        story.append(more_text_paragraph2)

        story.append(Spacer(5, 2/14 * inch))

        # Add signature and date
        signature_info1 = [
            [Paragraph(f"Date of Birth: <u><b>{context['client_dob']}</b></u>", underlined_style),
                Paragraph(
                f"Telephone: <u><b>{context['client_tel']}</b></u>", underlined_style),
                Paragraph(f"Email: <u><b>{context['client_email']}</b></u>", underlined_style)]
        ]
        signature_table1 = Table(signature_info1, colWidths=[
            1.8 * inch, 1.8 * inch, 2.5 * inch])
        signature_table1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(signature_table1)

        story.append(Spacer(5, 2/14 * inch))
        # Add more text
        more_text3 = """
        By typing your name in this space, you legally represent your real signature and acknowledge that the information provided is accurate and valid to the best of your knowledge.
        """
        more_text_paragraph3 = Paragraph(more_text3, paragraph_style)
        story.append(more_text_paragraph3)

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
        signature_table_data = [[signature_text, Spacer(0, 0.5), signature, Spacer(
            100, 0.5), date_paragraph]]
        signature_table = Table(signature_table_data, colWidths=[
                                70, None, 70, 100, 200])

        story.append(signature_table)

        return story

    def double_spanish(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        title = Paragraph(
            "CARTA DE CONSENTIMIENTO DE ACTUALIZACIÓN", title_style)
        story.append(title)

        # Add client name
        client_name = f"Yo, <u><b>{context['client_name']}</b></u>"
        client_name_paragraph = Paragraph(client_name, paragraph_style)
        story.append(client_name_paragraph)
        main_text = """
        estoy solicitando la asistencia de mis agentes <u><b>{}, NPN {} y {}, NPN {}</b></u>, autorizándoles a efectuar el siguiente cambio(cambios) en mi póliza <u><b>{}</b></u>, utilizando la información que he proporcionado.
        """.format(context['main_agent_name'], context['main_agent_npn'], context['secondary_agent_name'], context['secondary_agent_npn'], context['update_type'])
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))
        more_text_paragraph = Paragraph("Detalles del Plan", paragraph_style)
        story.append(more_text_paragraph)

        list_items = [
            f"Nombre del Plan: {context['client_plan_name']}",
            f"Prima Mensual: {context['client_monthly_payment']}",
            f"Deducible: {context['client_deductible']}",
            f"Gasto máximo de bolsillo: {context['client_max_out_pocket']}",
            f"Ingreso Total: {context['client_principal_income']}",
            f"Fecha de Vigencia: {context['client_effective_date']}",
        ]

        list_item_style = ParagraphStyle(
            name='ListItemStyle',
            parent=paragraph_style,
            leftIndent=10,
            spaceBefore=0,
            spaceAfter=1,
            bulletFontName='Helvetica',
        )
        for item in list_items:
            # Add whatever prefix you need
            paragraph = Paragraph(f"- {item}", list_item_style)
            story.append(paragraph)
        story.append(Spacer(5, 2/14 * inch))

        more_text = """
        Entiendo que mi consentimiento permanece vigente hasta que sea revocado o modificado poniéndome en contacto con el agente arriba mencionado y que mi información personal no será divulgada y será guardada de forma segura.

        Así mismo entiendo que en casos de cambios tales como:
        """.format(context['main_agent_name'])
        more_text_paragraph = Paragraph(more_text, paragraph_style)
        story.append(more_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))

        # Add a bullet list
        bullet_points = [
            "Estatus Marital.",
            "Cambios de Ingresos.",
            "Cambios en el número de personas en mi declaración de Impuestos.",
            "Cambios en el número de personas que necesitan cobertura médica en mi aplicación.",
            "Cambios de estatus migratorio.",
            "Cambios de dirección."
        ]

        bullet_list = ListFlowable(
            [ListItem(Paragraph(point))
                for point in bullet_points],
            bulletType='bullet',
            leftIndent=20,  # Adjust the left indentation
            spaceAfter=5,
        )
        story.append(bullet_list)

        # Add more text
        more_text2 = """
        Debo notificar a mi representante inmediatamente si ocurren estos cambios y sean actualizados en el Sistema.

        De la misma manera confirmo no tener otro seguro médico.
        """
        more_text_paragraph2 = Paragraph(more_text2, paragraph_style)
        story.append(more_text_paragraph2)

        story.append(Spacer(5, 2/14 * inch))

        # Add signature and date
        signature_info1 = [
            [Paragraph(f"Fecha de Nacimiento: <u><b>{context['client_dob']}</b></u>", underlined_style),
                Paragraph(
                f"Teléfono: <u><b>{context['client_tel']}</b></u>", underlined_style),
                Paragraph(f"Email: <u><b>{context['client_email']}</b></u>", underlined_style)]
        ]
        signature_table1 = Table(signature_info1, colWidths=[
            1.8 * inch, 1.8 * inch, 2.5 * inch])
        signature_table1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(signature_table1)

        story.append(Spacer(5, 2/14 * inch))
        # Add more text
        more_text3 = """
        Al firmar digitalmente escribiendo su nombre en este espacio, usted representa legalmente su firma real y reconoce que la información proporcionada es precisa y válida.
        """
        more_text_paragraph3 = Paragraph(more_text3, paragraph_style)
        story.append(more_text_paragraph3)

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
            f"Fecha de Firma: <font name='DancingScript' size='16'><u><b>{context['date_signature']}</b></u></font>", paragraph_style)

        signature_text = Paragraph("Firma:", paragraph_style)
        signature_table_data = [[signature_text, Spacer(0, 0.5), signature, Spacer(
            100, 0.5), date_paragraph]]
        signature_table = Table(signature_table_data, colWidths=[
                                50, None, 70, 100, 200])

        story.append(signature_table)
        return story

    def single_spanish(self, context, title_style, paragraph_style, bolded_style, underlined_style):
        story = []
        title = Paragraph(
            "CARTA DE CONSENTIMIENTO DE ACTUALIZACIÓN", title_style)
        story.append(title)

        # Add client name
        client_name = f"Yo, <u><b>{context['client_name']}</b></u>"
        client_name_paragraph = Paragraph(client_name, paragraph_style)
        story.append(client_name_paragraph)
        main_text = """
        estoy solicitando la asistencia de mi agente <u><b>{}, NPN {}</b></u>, autorizándole a efectuar el siguiente cambio(cambios) en mi póliza <u><b>{}</b></u>, utilizando la información que he proporcionado.
        """.format(context['main_agent_name'], context['main_agent_npn'], context['update_type'])
        main_text_paragraph = Paragraph(main_text, paragraph_style)
        story.append(main_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))
        more_text_paragraph = Paragraph("Detalles del Plan", paragraph_style)
        story.append(more_text_paragraph)

        list_items = [
            f"Nombre del Plan: {context['client_plan_name']}",
            f"Prima Mensual: {context['client_monthly_payment']}",
            f"Deducible: {context['client_deductible']}",
            f"Gasto máximo de bolsillo: {context['client_max_out_pocket']}",
            f"Ingreso Total: {context['client_principal_income']}",
            f"Fecha de Vigencia: {context['client_effective_date']}",
        ]

        list_item_style = ParagraphStyle(
            name='ListItemStyle',
            parent=paragraph_style,
            leftIndent=10,
            spaceBefore=0,
            spaceAfter=1,
            bulletFontName='Helvetica',
        )
        for item in list_items:
            # Add whatever prefix you need
            paragraph = Paragraph(f"- {item}", list_item_style)
            story.append(paragraph)
        story.append(Spacer(5, 2/14 * inch))

        more_text = """
        Entiendo que mi consentimiento permanece vigente hasta que sea revocado o modificado poniéndome en contacto con el agente arriba mencionado y que mi información personal no será divulgada y será guardada de forma segura.

        Así mismo entiendo que en casos de cambios tales como:
        """
        more_text_paragraph = Paragraph(more_text, paragraph_style)
        story.append(more_text_paragraph)

        story.append(Spacer(5, 2/14 * inch))

        # Add a bullet list
        bullet_points = [
            "Estatus Marital.",
            "Cambios de Ingresos.",
            "Cambios en el número de personas en mi declaración de Impuestos.",
            "Cambios en el número de personas que necesitan cobertura médica en mi aplicación.",
            "Cambios de estatus migratorio.",
            "Cambios de dirección."
        ]

        bullet_list = ListFlowable(
            [ListItem(Paragraph(point))
                for point in bullet_points],
            bulletType='bullet',
            leftIndent=20,  # Adjust the left indentation
            spaceAfter=5,
        )
        story.append(bullet_list)

        # Add more text
        more_text2 = """
        Debo notificar a mi representante inmediatamente si ocurren estos cambios y sean actualizados en el Sistema.

        De la misma manera confirmo no tener otro seguro médico.
        """
        more_text_paragraph2 = Paragraph(more_text2, paragraph_style)
        story.append(more_text_paragraph2)

        story.append(Spacer(5, 2/14 * inch))

        # Add signature and date
        signature_info1 = [
            [Paragraph(f"Fecha de Nacimiento: <u><b>{context['client_dob']}</b></u>", underlined_style),
                Paragraph(
                f"Teléfono: <u><b>{context['client_tel']}</b></u>", underlined_style),
                Paragraph(f"Email: <u><b>{context['client_email']}</b></u>", underlined_style)]
        ]
        signature_table1 = Table(signature_info1, colWidths=[
            1.8 * inch, 1.8 * inch, 2.5 * inch])
        signature_table1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(signature_table1)

        story.append(Spacer(5, 2/14 * inch))
        # Add more text
        more_text3 = """
        Al firmar digitalmente escribiendo su nombre en este espacio, usted representa legalmente su firma real y reconoce que la información proporcionada es precisa y válida.
        """
        more_text_paragraph3 = Paragraph(more_text3, paragraph_style)
        story.append(more_text_paragraph3)

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
        key = request.data.get('key', None)
        if not signature or not date_signature or not key:
            raise ValidationException('Missing signature')
        else:
            consent_log = ClientConsentLog.objects.filter(secret_key=key).get()
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
                    "date_signature": date_signature,
                    "client_name": consent_log.client_name,
                    "update_type": consent_log.update_type,
                    "client_id": consent_log.id_client,
                    "client_dob": dob,
                    "client_tel": consent_log.client_tel,
                    "client_email": consent_log.client_email,
                    "client_plan_name": consent_log.plan_name if consent_log.plan_name else '',
                    "client_monthly_payment": consent_log.monthly_payment if consent_log.monthly_payment else '0',
                    "client_deductible": consent_log.deductible if consent_log.deductible else '0',
                    "client_max_out_pocket": consent_log.max_out_pocket if consent_log.max_out_pocket else '0',
                    "client_principal_income": consent_log.principal_income if consent_log.principal_income else '0',
                    "main_agent_name": consent_log.main_agent_name,
                    "main_agent_npn": consent_log.main_agent_npn,
                    "main_agent_tel": consent_log.main_agent_tel,
                    "secondary_agent_name": consent_log.secondary_agent_name,
                    "secondary_agent_npn": consent_log.secondary_agent_npn,
                    "secondary_agent_tel": consent_log.secondary_agent_tel,
                    "client_effective_date": self.format_date(consent_log.effective_date) if consent_log.effective_date else ""
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
                    if consent_log.secondary_agent_name:
                        story = self.double_english(
                            context, title_style, paragraph_style, bolded_style, underlined_style)
                    else:
                        story = self.single_english(
                            context, title_style, paragraph_style, bolded_style, underlined_style)
                else:
                    if consent_log.secondary_agent_name:
                        story = self.double_spanish(
                            context, title_style, paragraph_style, bolded_style, underlined_style)
                    else:
                        story = self.single_spanish(
                            context, title_style, paragraph_style, bolded_style, underlined_style)

                # Add the main text

                doc.build(story)

                # Prepare the PDF file for download
                data = ClientDocument(
                    id_client=consent_log.id_client,
                    id_typedocument=10,
                    doc_name=''
                )
                data.doc_name.save(
                    f'{consent_log.client_name}_Update_Client_Consent.pdf', File(pdf_buffer))
                pdf_buffer.seek(0)
                consent_log.signed = True
                consent_log.date_signed = datetime.today()
                consent_log.save()
                return Response('Successfuly Submited', status=status.HTTP_200_OK)


class SendClientUpdateAgreementEmail(APIView):
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
            update_type = request.data.get('updateType', None)
            main_agent_npn = request.data.get('main_agent_npn', None)
            main_agent_tel = request.data.get('main_agent_tel', None)
            main_agent_name = request.data.get('main_agent_name', None)
            secondary_agent_npn = request.data.get('secondary_agent_npn', None)
            secondary_agent_tel = request.data.get('secondary_agent_tel', None)
            secondary_agent_name = request.data.get(
                'secondary_agent_name', None)
            secret_key = self.generate_random_key(32)
            if lan == 'Es':
                body = f"Tu agente: {agent.agent_name} {agent.agent_lastname}, le ha enviado este Acuerdo de Consentimiento para que lo firme. Puede llamar a su agente para confirmar que esto es oficial. Entre a este link para firmar el Consentimiento: {link}/sign_client_update_agreement?key={secret_key}"
            else:
                body = f"Your agent: {agent.agent_name} {agent.agent_lastname}, has sended you this Client Consent for you to sign. You can call your agent for confirmation that this is official. Enter to this URL to sign the Client Consent: {link}/sign_client_update_agreement?key={secret_key}"

            service = EmailService(user_name="Health Insurance",
                                   email=settings.EMAIL_HOST_USER, passw=settings.EMAIL_SAFEGUARD_PASSWORD)
            service.send_message(to, "Client Consent", False,
                                 None, None, None, body)
            monthly_payment, principal_income, max_out_pocket, deductible = get_client_int_fields(
                client)
            data = ClientConsentLog(
                id_client=id_client, id_agent=agent.id, agent_name=agent.agent_name + " " + agent.agent_lastname, client_name=client.names + " " + client.lastname, sended=True, year=date.today().year,
                lan=lan,
                main_agent_npn=main_agent_npn,
                update_type=update_type,
                main_agent_tel=main_agent_tel,
                main_agent_name=main_agent_name,
                client_dob=client.date_birth,
                client_tel=client.telephone,
                client_email=client.email,
                deductible=deductible,
                max_out_pocket=max_out_pocket,
                plan_name=client.new_plan,
                monthly_payment=monthly_payment,
                principal_income=principal_income,
                secondary_agent_npn=secondary_agent_npn,
                secondary_agent_tel=secondary_agent_tel,
                secondary_agent_name=secondary_agent_name,
                secret_key=secret_key,
                effective_date=client.aplication_date,
                date_sended=datetime.today()
            )

            data.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationException('Missing data')


def get_client_int_fields(client: Client):
    try:
        monthly_payment = float(client.aproxmontpay)
    except:
        monthly_payment = 0
    try:
        principal_income = float(client.princome)
        principal_income += float(client.conincome) if client.conincome else 0
    except:
        principal_income = 0
    try:
        max_out_pocket = float(client.max_out_pocket)
    except:
        max_out_pocket = 0
    try:
        deductible = float(client.deductible)
    except:
        deductible = 0

    return monthly_payment, principal_income, max_out_pocket, deductible


class SendUpdateClientAgreementSMSView(APIView, SmsCommons, Common):
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
                update_type = request.data.get('updateType', None)
                main_agent_npn = request.data.get('main_agent_npn', None)
                main_agent_tel = request.data.get('main_agent_tel', None)
                main_agent_name = request.data.get('main_agent_name', None)
                secondary_agent_npn = request.data.get(
                    'secondary_agent_npn', None)
                secondary_agent_tel = request.data.get(
                    'secondary_agent_tel', None)
                secondary_agent_name = request.data.get(
                    'secondary_agent_name', None)
                secret_key = self.generate_random_key(32)
                if lan == 'Es':
                    body = f"Tu agente: {agent.agent_name} {agent.agent_lastname}, le ha enviado este Acuerdo de Consentimiento para que lo firme. Puede llamar a su agente para confirmar que esto es oficial. Entre a este link para firmar el Consentimiento: {link}/sign_client_update_agreement?key={secret_key}"
                else:
                    body = f"Your agent: {agent.agent_name} {agent.agent_lastname}, has sended you this Client Consent for you to sign. You can call your agent for confirmation that this is official. Enter to this URL to sign the Client Consent: {link}/sign_client_update_agreement?key={secret_key}"

                message = service.send_custom_sms(
                    from_=company_number, to=to, sms=body)
            monthly_payment, principal_income, max_out_pocket, deductible = get_client_int_fields(
                client)
            if message:
                data = ClientConsentLog(
                    id_client=id_client, id_agent=agent.id, agent_name=agent.agent_name + " " + agent.agent_lastname, client_name=client.names + " " + client.lastname, sended=True, year=date.today().year,
                    lan=lan,
                    update_type=update_type,
                    main_agent_npn=main_agent_npn,
                    main_agent_tel=main_agent_tel,
                    main_agent_name=main_agent_name,
                    client_dob=client.date_birth,
                    client_tel=client.telephone,
                    client_email=client.email,
                    deductible=deductible,
                    max_out_pocket=max_out_pocket,
                    plan_name=client.new_plan,
                    monthly_payment=monthly_payment,
                    principal_income=principal_income,
                    secondary_agent_npn=secondary_agent_npn,
                    secondary_agent_tel=secondary_agent_tel,
                    secondary_agent_name=secondary_agent_name,
                    secret_key=secret_key,
                    effective_date=client.aplication_date,
                    date_sended=datetime.today()
                )

                data.save()
                result = Response('Sended',
                                  status=status.HTTP_200_OK,
                                  )
            else:
                raise ValidationException('Not Sended')
            return result
