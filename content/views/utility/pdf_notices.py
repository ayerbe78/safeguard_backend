from ..imports import *


class PDFNoticeViewSet(viewsets.ModelViewSet, Common):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PDFNoticeSerializer
    queryset = PDFNotice.objects.all()
