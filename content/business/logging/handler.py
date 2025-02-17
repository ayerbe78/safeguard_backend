import json
import time
from django.urls import resolve
from django.utils import timezone
from .utils import *
from content.models import ApiLog
from django.db.utils import OperationalError
from django.contrib.auth.models import AnonymousUser
import logging
import traceback

logger = logging.getLogger("django")


class APILoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

        self.DRF_API_LOGGER_PATH_TYPE = "ABSOLUTE"

        self.DRF_API_LOGGER_SKIP_URL_NAME = []

        self.DRF_API_LOGGER_SKIP_NAMESPACE = []

        self.DRF_API_LOGGER_METHODS = ["POST", "PUT", "DELETE", "PATCH"]

        self.DRF_API_LOGGER_STATUS_CODES = []

    def __call__(self, request):

        # Run only if logger is enabled.

        url_name = resolve(request.path_info).url_name
        namespace = resolve(request.path_info).namespace

        # Always skip Admin panel

        if namespace == "admin":
            return self.get_response(request)
        # Skip for url name
        if url_name in self.DRF_API_LOGGER_SKIP_URL_NAME:
            return self.get_response(request)
        # Skip entire app using namespace
        if namespace in self.DRF_API_LOGGER_SKIP_NAMESPACE:
            return self.get_response(request)
        start_time = time.time()
        request_data = self.__get_body(request)
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        # Only log required status codes if matching
        if (
            self.DRF_API_LOGGER_STATUS_CODES
            and response.status_code not in self.DRF_API_LOGGER_STATUS_CODES
        ):
            return response

        # Code to be executed for each request/response after
        # the view is called.

        headers, method = self.__get_headers_method(request)

        # Log only registered methods if available.
        if (
            len(self.DRF_API_LOGGER_METHODS) > 0
            and method not in self.DRF_API_LOGGER_METHODS
        ):
            return response

        if (
            response.get("content-type")
            in (
                "application/json",
                "application/vnd.api+json",
                "application/gzip",
            )
            or response.get("content-type") == None
        ):

            if response.get("content-type") == "application/gzip":
                response_body = "** GZIP Archive **"
            elif getattr(response, "streaming", False):
                response_body = "** Streaming **"
            elif response.get("content-type") == None:
                response_body = "** No Content **"
            else:
                if type(response.content) == bytes:
                    response_body = json.loads(response.content.decode())
                else:
                    response_body = json.loads(response.content)

            api = self.__get_api(request)
            # Get the request user
            user, user_email = self.__get_user_usermail(request)

            data = dict(
                api=mask_sensitive_data(api, mask_api_parameters=True),
                headers=mask_sensitive_data(headers),
                body=mask_sensitive_data(request_data),
                method=method,
                client_ip_address=get_client_ip(request),
                response=mask_sensitive_data(response_body),
                status_code=response.status_code,
                execution_time=time.time() - start_time,
                added_on=timezone.now(),
                user=user,
                user_email=user_email,
            )
            d = data.copy()
            d["headers"] = json.dumps(d["headers"], indent=4, ensure_ascii=False)
            if request_data:
                d["body"] = json.dumps(d["body"], indent=4, ensure_ascii=False)
            d["response"] = json.dumps(d["response"], indent=4, ensure_ascii=False)

            self.__store_to_db(d)
        else:
            return response
        return response

    def process_exception(self, request, exception):
        """This function is called whenever an exception happens"""
        start_time = time.time()
        request_data = self.__get_body(request)
        headers, method = self.__get_headers_method(request)
        api = self.__get_api(request)
        user, user_email = self.__get_user_usermail(request)

        tb = exception.__traceback__
        tb_str = traceback.format_exception(type(exception), exception, tb)
        if exception.__str__() == "":
            exc_text = tb_str
        else:
            exc_text = exception.__str__()
        response_body = f"""Exception:{exc_text}"""

        data = dict(
            api=mask_sensitive_data(api, mask_api_parameters=True),
            headers=mask_sensitive_data(headers),
            body=mask_sensitive_data(request_data),
            method=method,
            client_ip_address=get_client_ip(request),
            response=mask_sensitive_data(response_body),
            status_code=500,
            execution_time=time.time() - start_time,
            added_on=timezone.now(),
            user=user,
            user_email=user_email,
        )
        d = data.copy()
        d["headers"] = json.dumps(d["headers"], indent=4, ensure_ascii=False)
        if request_data:
            d["body"] = json.dumps(d["body"], indent=4, ensure_ascii=False)
        d["response"] = json.dumps(d["response"], indent=4, ensure_ascii=False)
        self.__store_to_db(d)
        return None

    def __get_headers_method(self, request):
        headers = get_headers(request=request)
        method = request.method

        return headers, method

    def __get_user_usermail(self, request):
        user = get_current_user(request)
        try:
            if isinstance(user, AnonymousUser):
                user = None
                user_email = None
            else:
                user_email = user.email
        except:
            user = None
            user_email = None

        return user, user_email

    def __get_api(self, request):
        if self.DRF_API_LOGGER_PATH_TYPE == "ABSOLUTE":
            api = request.build_absolute_uri()
        elif self.DRF_API_LOGGER_PATH_TYPE == "FULL_PATH":
            api = request.get_full_path()
        elif self.DRF_API_LOGGER_PATH_TYPE == "RAW_URI":
            api = request.get_raw_uri()
        else:
            api = request.build_absolute_uri()

        return api

    def __get_body(self, request):
        request_data = ""
        try:
            request_data = json.loads(request.body) if request.body else ""
        except:
            pass
        return request_data

    def __store_to_db(self, data):
        try:
            ApiLog.objects.create(**data)
        except OperationalError as e:
            raise Exception(e)
        except Exception as e:
            logger.error("DRF API LOGGER EXCEPTION:", e)
