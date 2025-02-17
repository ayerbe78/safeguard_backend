import time
import pytz
from email.mime.message import MIMEMessage
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib as smtp
from imap_tools import MailBox, MailMessage, MailAttachment, AND, A, MailMessageFlags
import csv
from email.policy import default
from math import ceil, floor
from select import select
from django.db import connection
from django.forms.models import model_to_dict

from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
from content.models import *
from content.serializers import *
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request as APIViewRequest
from rest_framework import status
from datetime import date, datetime
from customauth.GroupsPermission import *
from customauth.models import CustomUser
from customauth.serializers import (
    ListUserSerializer,
    RegisterSerializer,
    UserSerializer,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
import io
from django.http import FileResponse, HttpRequest
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A3, A4, A2, A1
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table, TableStyle, colors
from django.db import transaction
from django.db.models import Max, Sum, Q, F, Value as V, Count
from django.db.models.functions import Concat
from django.contrib.auth.models import Group
from content.business.business import *
from content.business.exceptions.custom_exceptions import *

import logging

logger = logging.getLogger("django")
