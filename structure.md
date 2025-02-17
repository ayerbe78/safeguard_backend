# Estructura

## General

> Estructura del arbol de directorios general

```
├───content(codigo con la logica del negocio)
│   ├───business(clases comunes y logica comun a utilizar en toda la app)
│   │   ├───exceptions(excepciones comunes en la app)
│   ├───views(implementacion de vistas o endpints de la aplicacion)
│   │   ├───mailing
│   │   │   ├───service
│   │   │   │   ├───models
│   │   ├───main
│   │   ├───reports
│   │   ├───settings
│   │   ├───sms
│   │   │   ├───models
│   │   │   ├───service
│   │   ├───test
│   │   ├───utility
├───customauth(codigo para la autenticacion y autorizacion en la app)
├───logs(logs de la aplicacion)
│   ├───errors
│   └───info
├───media
└───safeguard(configuraciones de la app)
```

## Específico

### content

- #### content/business

> Estructura

```
│   business.py
│
├───exceptions
│   │   custom_exceptions.py
│   │   Handler.py
```

En _`business.py`_ se encuentran clases comunes con funcionalidades reutilizables en toda la logica de la aplicacion incluyendo la clase `AgencyManagement` que se encarga de la obtencion de los recursos del negocio (clientes, agentes, agencias, etc...) que le corresponde a cada usuario que solicita algun request.

Hay otras clases comunes y utiles para ejecutar sql, informacion de pagos,...

En `custom_exceptions.py` se encuentran excepciones personalizadas y comunes que se utilizan en la aplicacion

- #### content/views

> Estructura

```
│   imports.py
│   views.py
│
├───mailing
│   │   mail_credentials.py
│   │   views.py
│   │
│   ├───service
│   │   │   email_service.py
│   │   │
│   │   ├───models
│   │   │   │   email_attach.py
│   │   │   │   email_message.py
│
├───main
│   │   agent.py
│   │   application.py
│   │   assistant.py
│   │   bobglobal.py
│   │   client.py
│   │   views.py
│   │   __common.py
│
├───reports
│   │   chart_data.py
│   │   clients_by_company.py
│   │   insurance_payment_balance.py
│   │   paymentagent.py
│   │   paymentassistant.py
│   │   paymentclient.py
│   │   payment_agency.py
│   │   payment_discrepancy.py
│   │   payment_insured_only.py
│   │   payment_override_assistant.py
│   │   pending_documents.py
│   │   views.py
│
├───settings
│   │   agency.py
│   │   agent_commission.py
│   │   city.py
│   │   commissions_group.py
│   │   commission_agency.py
│   │   county.py
│   │   document_type.py
│   │   event.py
│   │   group.py
│   │   group_commission.py
│   │   health_plan.py
│   │   insured.py
│   │   language.py
│   │   plan_name.py
│   │   policy.py
│   │   product.py
│   │   soc_service_referral.py
│   │   special_election.py
│   │   state.py
│   │   status.py
│   │   type.py
│   │   views.py
│   │   _commons.py
│
├───sms
│   │   views.py
│   │
│   ├───models
│   │   │   sms_models.py
│   │   │   sms_serializer.py
│   │
│   ├───service
│   │   │   sms_service.py
│   │   │   sms_temp_file.py
│
├───utility
│   │   birthdays.py
│   │   claims.py
│   │   videos.py
│   │   views.py
```

- mailing
  - todos los servicios relacionados con el correo en la aplicacion. inluyendo los modelos necesarios
  - se encuentran separados como tal el servicio de correo de un fichero para la configuracion de correo para el usuario
- main
  - cada uno de los ficheros poseen los `model.ViewSet` de sus respectivos modelos y recursos de la app asi como los directamente relacionados con ellos
  - el fichero `_commons.py` posee clases y metodos comunes para varios de estos ficheros
- reports
  - cada uno de los ficheros se asocian a los diferentes reportes que debe generar la aplicacion
  - en cada fichero se encuentra todas las variables de un reporte(normal, resumen, pdf, csv)
  - estan los reportes que se utilizan en el dashboard del front end
- settings
  - estan todos los viewSets de las opciones del negocio separados por su correspondiente fichero
- sms
  - todos los ficheros relacionados con el servicio de sms de la aplicacion
- utility
  - algunos de los servicios del negocio que no entran en las anteriores categorias
  - son endpoints utlizados en varias partes del frontend
- _import.py_
  - estan todos los imports que se utilizaban previamente en el enorme fichero `views.py` global y es el q seimporta en cada uno de los ficheros de clases
- _views.py_
  - es el fichero de views global del cual se extraen las _ApiViews_ que se usan en el mapeo con urls de la aplicacion.
  - estan los imports de cada `views.py` de los subdirectorios
  - ademas estan algunos metodos que faltan por migrar a sus corespondientes ficheros especificos

#### Nota

> el fichero `views.py` importa todas las APIView's de cada directorio y es el que se importa en el `views.py` global

- #### content/

> Estructura

```
...
│   admin.py
│   apps.py
│   models.py
│   serializers.py
│   tests.py
│   urls.py
...
```

- en `models.py` estan los modelos del negocio
- en `serializers.py` eston los serilizers
- en `urls.py` estan los mapeos a url de las distintas clases

### customauth

> Estructura

```
│   admin.py
│   apps.py
│   GroupsPermission.py
│   models.py
│   serializers.py
│   tests.py
│   urls.py
│   views.py
```

- En `models.py` estan los modelos relacionados con la autenticacion, incluidos los modelos de _CustomUser_ y _Groups_
- En `serializers.py` estan los serializers
- En `GroupsPermission.py` estan todas las clases de permisos para cada una de las vistas tanto de customauth como de content
- En `views.py` estan todas las Vistas o endpoints relacionadas con la gestion de usuarios y permisos
- En `urls.py` estan los mapeos de las vistas de customauth a endpoints
