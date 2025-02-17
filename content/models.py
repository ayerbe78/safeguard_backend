from django.db import models
from customauth.models import CustomUser

# Models matching the existing tables in the database

# SETTINGS


class Agency(models.Model):
    # Strings
    agency_name = models.CharField(max_length=100, blank=True)
    agency_address = models.TextField(blank=True)
    agency_phone = models.CharField(max_length=15, blank=True)
    agency_email = models.CharField(max_length=150, blank=True)
    agency_number = models.CharField(max_length=255, blank=True)
    agency_bank = models.CharField(max_length=150, blank=True)
    agency_account = models.CharField(max_length=50, blank=True)
    agency_person = models.CharField(max_length=150, blank=True)
    lavel = models.CharField(max_length=15, blank=True, null=True)
    # ForeignKeys
    parent_id = models.IntegerField(blank=True, null=True)
    admin_id = models.IntegerField(blank=True, null=True)

    self_managed = models.BooleanField(null=True, default=False)

    class Meta:
        managed = False
        db_table = "agency"


class DocumentType(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "document_type"


class Event(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "event"


class Groups(models.Model):
    names = models.CharField(max_length=100)
    tipo_grupo = models.IntegerField()

    class Meta:
        managed = False
        db_table = "groups"


class HealthPlan(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "health_plan"


class Insured(models.Model):
    # Strings
    names = models.CharField(max_length=50)
    color = models.CharField(max_length=15)
    # Numbers
    com_new = models.DecimalField(max_digits=10, decimal_places=2)
    com_reva = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.IntegerField()
    # Files
    logo = models.ImageField(null=True, blank=True, default=None)

    class Meta:
        managed = False
        db_table = "insured"


class Language(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "language"


class PlanName(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "plan_name"


class Poliza(models.Model):
    names = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = "poliza"


class Product(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "product"


class Sendsms(models.Model):
    # Strings
    sto = models.CharField(max_length=30)
    sbody = models.CharField(max_length=250, db_collation="utf8mb4_general_ci")
    sid = models.CharField(max_length=100)
    status = models.CharField(max_length=15)
    sfrom = models.CharField(max_length=45, blank=True, null=True)
    # Dates
    timestamp = models.DateTimeField(blank=True, null=True)
    # Files
    imagen = models.CharField(max_length=250, blank=True, null=True)
    # Numbers
    sread = models.IntegerField()

    class Meta:
        managed = False
        db_table = "sendsms"


class SocServiceRefe(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "soc_service_refe"


class SpecialElection(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "special_election"


class State(models.Model):
    # Strings
    names = models.CharField(max_length=50)
    sigla = models.CharField(max_length=2)
    # Numbers
    com_new = models.DecimalField(max_digits=12, decimal_places=2)
    com_reva = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "state"


class Status(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "status"


class Type(models.Model):
    names = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "type"


class TypePendingdoc(models.Model):
    names = models.CharField(max_length=50, db_collation="utf8_general_ci")

    class Meta:
        managed = False
        db_table = "type_pendingdoc"


class Video(models.Model):
    names = models.CharField(max_length=50)
    path = models.CharField(max_length=255)
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "video"


class City(models.Model):
    # id_state = models.IntegerField(null=True)
    names = models.CharField(max_length=50)
    id_state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        db_column="id_state",
        related_name="cities",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "city"


class County(models.Model):
    # id_city = models.ForeignKey(City, models.DO_NOTHING, db_column="id_city")
    names = models.CharField(max_length=50)
    id_city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        db_column="id_city",
        related_name="counties",
        null=True,
    )

    class Meta:
        managed = False
        db_table = "county"


class CommAgent(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField()
    id_insured = models.IntegerField()
    id_state = models.IntegerField()
    # Numbers
    comm_new = models.DecimalField(max_digits=10, decimal_places=2)
    comm_rew = models.DecimalField(max_digits=10, decimal_places=2)
    comm_set = models.DecimalField(max_digits=10, decimal_places=2)
    comm_set2 = models.DecimalField(max_digits=10, decimal_places=2)
    # Strings
    yearcom = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = "comm_agent"


class CommAgency(models.Model):
    # ForeignKeys
    # id_agency = models.IntegerField()
    id_agency = models.ForeignKey(
        Agency,
        on_delete=models.SET_NULL,
        db_column="id_agency",
        related_name="commissions",
        null=True,
    )
    # id_insured = models.IntegerField()
    id_insured = models.ForeignKey(
        Insured,
        on_delete=models.SET_NULL,
        db_column="id_insured",
        related_name="cities",
        null=True,
    )
    # Numbers
    comm = models.DecimalField(max_digits=10, decimal_places=2)
    # Strings
    yearcom = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = "comm_agency"


# MAIN


class Assistant(models.Model):
    password = models.TextField(blank=True)
    assistant_name = models.CharField(
        max_length=50, db_collation="utf8_general_ci", blank=True
    )
    assistant_lastname = models.CharField(
        max_length=50, db_collation="utf8_general_ci", blank=True
    )
    telephone = models.CharField(
        max_length=50, db_collation="utf8_general_ci", blank=True
    )
    email = models.CharField(
        max_length=50, db_collation="utf8_general_ci", blank=True)
    email2 = models.CharField(
        max_length=50, db_collation="utf8_general_ci", blank=True)
    comition = models.FloatField(blank=True)
    borrado = models.BooleanField(default=False, null=True, blank=True)

    agency = models.ForeignKey(
        Agency, on_delete=models.DO_NOTHING, db_column="id_agency", null=True
    )

    class Meta:
        managed = False
        db_table = "assistant"


class Subassistant(models.Model):
    password = models.TextField()
    assistant_name = models.CharField(max_length=50)
    assistant_lastname = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    email2 = models.CharField(max_length=50)
    id_assistant = models.IntegerField()

    class Meta:
        managed = False
        db_table = "subassistant"


class CommissionsGroup(models.Model):
    names = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = "commissions_group"


class Agent(models.Model):
    # ForeignKeys
    id_assistant = models.IntegerField(blank=True, default=0)
    id_county = models.ForeignKey(
        "County", models.DO_NOTHING, db_column="id_county")
    id_agency = models.IntegerField(blank=True)
    id_group = models.IntegerField(blank=True)  # remove
    id_group2 = models.IntegerField(blank=True)  # remove
    commission_group = models.ForeignKey(
        CommissionsGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column="id_commission_group",
        related_name="agents",
    )
    # Strings
    agent_name = models.CharField(max_length=50, blank=True)
    agent_lastname = models.CharField(max_length=50, blank=True)
    comments = models.CharField(max_length=250, blank=True)
    license_number = models.CharField(max_length=10, blank=True)
    npn = models.CharField(max_length=15, blank=True)
    telephone = models.CharField(max_length=15, blank=True)
    email = models.CharField(max_length=200, blank=True)
    email2 = models.CharField(max_length=150, blank=True)
    agent_number = models.CharField(max_length=10, blank=True)
    humana_san = models.CharField(max_length=10, blank=True)
    password = models.TextField()
    core = models.CharField(max_length=10, blank=True)
    relase_coment = models.CharField(max_length=250, blank=True)
    telephone2 = models.CharField(max_length=15, blank=True)
    socialsecurity = models.CharField(max_length=15, blank=True)
    adreess = models.CharField(max_length=255, blank=True)
    # Field name made lowercase.
    passsherpa = models.CharField(
        db_column="passSherpa", max_length=50, blank=True)
    # Field name made lowercase.
    user1sherpa = models.CharField(
        db_column="user1Sherpa", max_length=100, blank=True)
    # Field name made lowercase.
    user2sherpa = models.CharField(
        db_column="user2Sherpa", max_length=100, blank=True)
    # Field name made lowercase.
    pass2sherpa = models.CharField(
        db_column="pass2Sherpa", max_length=100, blank=True)
    # Field name made lowercase.
    usercms = models.CharField(db_column="userCMS", max_length=50, blank=True)
    # Field name made lowercase.
    passcms = models.CharField(db_column="passCMS", max_length=50, blank=True)
    pregunta = models.CharField(max_length=255, blank=True)
    pregunta1 = models.CharField(max_length=255, blank=True)
    pregunta2 = models.CharField(max_length=255, blank=True)
    back_name = models.CharField(max_length=30, blank=True)
    router_number = models.CharField(max_length=30, blank=True)
    back_account = models.CharField(max_length=30, blank=True)
    polyce_number = models.CharField(max_length=30, blank=True)
    aca_certificate_number = models.CharField(max_length=200, blank=True)
    napa_certificate_number = models.CharField(max_length=200, blank=True)
    # Numbers
    released = models.IntegerField(blank=True)
    ahip = models.IntegerField(blank=True)
    administrator = models.IntegerField(blank=True)
    typepay = models.IntegerField(blank=True)
    maneger = models.IntegerField(blank=True, null=True)  # remove
    director = models.IntegerField(blank=True, null=True)  # remove
    com_maneger = models.IntegerField(blank=True, null=True)  # remove
    com_director = models.IntegerField(blank=True, null=True)  # remove
    type_account = models.IntegerField(blank=True)
    adminagency = models.IntegerField(blank=True)
    borrado = models.IntegerField(blank=True, default=0)
    des_oep = models.DecimalField(max_digits=15, decimal_places=0, blank=True)
    des_renewal = models.DecimalField(
        max_digits=15, decimal_places=0, blank=True)
    # Dates
    ahip_date_start = models.DateField(blank=True)
    ahip_date_renewal = models.DateField(blank=True)
    date_start = models.DateField(blank=True)
    date_birth = models.DateField(blank=True)
    efective_certificate = models.DateField(blank=True)
    end_certificate = models.DateField(blank=True)
    aca_date_certification = models.DateField(blank=True)
    napa_date_certification = models.DateField(blank=True)
    # Booleans
    aca = models.BooleanField(blank=True)
    napa = models.BooleanField(blank=True)
    cms = models.BooleanField(blank=True)
    sherpa = models.BooleanField(blank=True)
    medicare = models.BooleanField(blank=True)
    life_insurance = models.BooleanField(blank=True)
    secondary_agent = models.BooleanField(blank=True, null=True, default=None)
    exclusive_secondary_agent = models.BooleanField(
        blank=True, null=True, default=None)
    send_discrepancies = models.BooleanField(
        blank=True, null=True, default=None)
    # Files
    document = models.FileField(blank=True)
    file = models.FileField(blank=True, null=True)
    # DynamicFields
    fields = models.JSONField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "agent"
        permissions = (
            ("export_pdf_agent", "Can Export Agent PDF"),
            ("export_excel_agent", "Can Export Agent Excel"),
        )


class AgentDocument(models.Model):
    id_agent = models.IntegerField()
    file = models.FileField()

    class Meta:
        managed = False
        db_table = "agent_document"


class AgentTaxDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_agent = models.IntegerField()
    file = models.FileField()

    class Meta:
        managed = False
        db_table = "agent_tax_document"


class AgentState(models.Model):
    id_agent = models.ForeignKey(
        Agent, models.DO_NOTHING, db_column="id_agent")
    id_state = models.ForeignKey(
        State, models.DO_NOTHING, db_column="id_state"
    )

    class Meta:
        managed = False
        db_table = "agent_state"


class Application(models.Model):
    # ForeignKeys
    a = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "application"
        permissions = (
            ("export_pdf_application", "Can Export Application PDF"),
            ("export_excel_application", "Can Export Application Excel"),
        )


class Client(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField(blank=True)
    id_status = models.IntegerField(blank=True)
    id_poliza = models.IntegerField(blank=True, null=True)
    id_insured = models.IntegerField(blank=True)
    id_state = models.IntegerField(blank=True, null=True)
    id_event = models.IntegerField(blank=True)
    # Strings
    names = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=150, blank=True)
    social_security = models.CharField(max_length=12, blank=True, null=True)
    suscriberid = models.CharField(max_length=15, blank=True)
    marketplace_user = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    application_id = models.CharField(max_length=15, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True)
    email = models.CharField(max_length=150, blank=True)
    addreess = models.CharField(max_length=250, blank=True, null=True)
    agent2 = models.CharField(max_length=150, blank=True)
    alien = models.CharField(max_length=50, blank=True, null=True)
    src = models.CharField(max_length=50, blank=True, null=True)
    card = models.CharField(max_length=50, blank=True, null=True)
    catagory = models.CharField(max_length=50, blank=True, null=True)
    folio = models.CharField(max_length=50, blank=True, null=True)
    depature = models.CharField(max_length=50, blank=True, null=True)
    princome = models.CharField(blank=True, max_length=50)
    conincome = models.CharField(blank=True, max_length=50)
    teltrabajo = models.CharField(blank=True, max_length=30)
    nomtrabajo = models.CharField(blank=True, max_length=100)
    totalincome = models.CharField(blank=True, max_length=100)
    aproxmontpay = models.CharField(blank=True, max_length=100)
    plansupp = models.CharField(blank=True, max_length=255, null=True)
    new_plan = models.CharField(blank=True, max_length=255, null=True)
    usermark = models.CharField(blank=True, max_length=100)
    usermarkpw = models.CharField(blank=True, max_length=100)
    ccnumber = models.CharField(blank=True, max_length=25)
    expdate = models.CharField(blank=True, max_length=255)
    toname = models.CharField(blank=True, max_length=100)
    billingaddreess = models.CharField(blank=True, max_length=250)
    bank = models.CharField(blank=True, max_length=100)
    bankacc = models.CharField(blank=True, max_length=100)
    routing = models.CharField(blank=True, max_length=255)
    paymentconf = models.CharField(blank=True, max_length=50)
    nameinsurance = models.CharField(blank=True, max_length=100)
    worked_by = models.CharField(blank=True, max_length=50)
    app_problem_note = models.CharField(blank=True, null=True, max_length=500)
    # Numbers
    family_menber = models.IntegerField(blank=True, null=True)
    pending = models.IntegerField(blank=True, default=0)
    income = models.IntegerField(blank=True, default=0)
    migratory_status = models.IntegerField(blank=True, default=0)
    social_security_doc = models.IntegerField(blank=True, default=0)
    loss_medicaiad = models.IntegerField(blank=True, default=0)
    pendingno = models.IntegerField(blank=True, default=0)
    borrado = models.IntegerField(blank=True, default=0)
    coverage = models.IntegerField(blank=True, default=0)
    sexo = models.IntegerField(blank=True, default=0)
    new_ren = models.IntegerField(blank=True, default=0)
    priw21099 = models.IntegerField(blank=True, default=0)
    targeta = models.IntegerField(blank=True, default=0)
    targetatipo = models.IntegerField(blank=True, default=0)
    cvccode = models.CharField(blank=True, max_length=3)
    automaticpay = models.IntegerField(blank=True, default=0)
    w2principal = models.IntegerField(blank=True, default=0)
    w2conyugue = models.IntegerField(blank=True, default=0)
    tipoclient = models.IntegerField(blank=True, default=0)
    acepto = models.IntegerField(blank=True, default=0)
    unemprincipal = models.IntegerField(blank=True, default=0)
    unemconyugue = models.IntegerField(blank=True, default=0)
    percent = models.DecimalField(
        max_digits=10, decimal_places=0, blank=True, default=0, null=True
    )
    agent_pay = models.DecimalField(
        max_digits=10, decimal_places=0, blank=True, default=0, null=True
    )
    mo_premium = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, default=0, null=True
    )
    mensualidad = models.FloatField(blank=True, default=0)
    payment = models.FloatField(blank=True, default=0)
    deductible = models.FloatField(blank=True, null=True)
    max_out_pocket = models.FloatField(blank=True, null=True)
    # Dates
    aplication_date = models.DateField(blank=True)
    paid_date = models.DateField(blank=True, null=True)
    fechaexdition = models.DateField(blank=True, null=True)
    date_birth = models.DateField(blank=True)
    fechacreado = models.DateField(blank=True, auto_now_add=True)
    # Field name made lowercase.
    fechainsert = models.DateField(
        db_column="fechaInsert", blank=True, auto_now_add=True
    )
    paymentday = models.DateField(blank=True, null=True)
    cardexp = models.DateField(blank=True, default="1000-01-01", null=True)
    hora = models.TimeField(blank=True, auto_now_add=True)
    sended_to_assistant = models.DateTimeField(blank=True, null=True)
    # Files
    # Field name made lowercase.
    photo = models.CharField(
        db_column="Photo", max_length=50, blank=True, null=True)
    document = models.FileField(blank=True, null=True)

    # Booleans
    not_visible = models.BooleanField(default=None, null=True, blank=True)
    renewed = models.BooleanField(default=None, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "client"
        permissions = (
            ("export_pdf_client", "Can Export Client PDF"),
            ("export_excel_client", "Can Export Client Excel"),
        )


class Medicare(models.Model):
    # ForeignKeys
    id_city = models.IntegerField()
    id_state = models.IntegerField()
    id_county = models.IntegerField()
    id_special_election = models.IntegerField()
    id_agency = models.IntegerField()
    id_soc_service_ref = models.IntegerField()
    id_type = models.IntegerField()
    id_plan_name = models.IntegerField()
    id_agent = models.IntegerField()
    id_healthplan = models.IntegerField()
    # Strings
    names = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    zip_code = models.CharField(max_length=15)
    email = models.CharField(max_length=150)
    gender = models.CharField(max_length=1)
    phone = models.CharField(max_length=30)
    name_card = models.CharField(max_length=150)
    medicare_id = models.CharField(max_length=50)
    prim_care_phis_name = models.CharField(max_length=150)
    primary_care_id = models.CharField(max_length=50)
    prim_care_address = models.CharField(max_length=150)
    pref_special_name = models.CharField(max_length=150)
    take_medication = models.CharField(max_length=250)
    prefe_health_plan_one = models.CharField(max_length=150)
    prefe_health_plan_two = models.CharField(max_length=150)
    remark = models.TextField()
    # Numbers
    medicaid_number = models.IntegerField()
    time_reciden = models.IntegerField()
    # Dates
    dob = models.DateField()
    part_a_date = models.DateField()
    part_b_date = models.DateField()
    application_date = models.DateField()
    signature_date = models.DateField()

    class Meta:
        managed = False
        db_table = "medicare"


# SocialSecurity
class ClientMedicare(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField()
    # Strings
    names = models.CharField(max_length=50, db_collation="utf8_general_ci")
    lastname = models.CharField(max_length=150, db_collation="utf8_general_ci")
    address = models.CharField(max_length=250, db_collation="utf8_general_ci")
    telephone = models.CharField(max_length=15, db_collation="utf8_general_ci")
    secundary_telephone = models.CharField(
        max_length=15, db_collation="utf8_general_ci"
    )
    email = models.CharField(max_length=150, db_collation="utf8_general_ci")
    social_security = models.CharField(
        max_length=12, db_collation="utf8_general_ci")
    medicare_number = models.CharField(
        max_length=12, db_collation="utf8_general_ci")
    medicaid_number = models.CharField(
        max_length=12, db_collation="utf8_general_ci")
    document = models.FileField()
    remark = models.CharField(max_length=250, db_collation="utf8_general_ci")
    # Numbers
    medicaid_level = models.IntegerField()
    supplementary = models.IntegerField()
    foodstamp = models.DecimalField(max_digits=10, decimal_places=0)
    # Dates
    year_entry = models.DateField()
    date_birth = models.DateField()
    part_a_date = models.DateField()
    part_b_date = models.DateField()
    closed_date = models.DateField()
    initial_date = models.DateField()

    class Meta:
        managed = False
        db_table = "client_medicare"


class ProspectManager(models.Model):
    # ForeignKeys
    id_product = models.IntegerField()
    id_agent = models.IntegerField()
    idstatus = models.IntegerField()
    # Strings
    name = models.CharField(max_length=50, db_collation="latin1_swedish_ci")
    last_name = models.CharField(
        max_length=100, db_collation="latin1_swedish_ci")
    telephone = models.CharField(
        max_length=50, db_collation="latin1_swedish_ci")
    address = models.CharField(
        max_length=250, db_collation="latin1_swedish_ci")
    email = models.CharField(max_length=150, db_collation="latin1_swedish_ci")
    referred = models.CharField(
        max_length=50, db_collation="latin1_swedish_ci")
    # Dates
    date_brith = models.DateField()

    class Meta:
        managed = False
        db_table = "prost_maneger"


# Document


class Updocument(models.Model):
    id_agent = models.IntegerField()
    id_insuerd = models.IntegerField()
    fecha = models.DateField()
    document = models.FileField()

    class Meta:
        managed = False
        db_table = "updocument"


class BobGlobal(models.Model):
    # ForeignKeys
    id_insured = models.IntegerField()
    # Strings
    agent_name = models.CharField(max_length=100)
    agent_npn = models.CharField(max_length=100, blank=True, null=True)
    client_name = models.CharField(max_length=50)
    client_lastname = models.CharField(max_length=50)
    suscriberid = models.CharField(max_length=15)
    num_members = models.CharField(max_length=3, blank=True, null=True)
    pol_hold_state = models.CharField(max_length=5, blank=True, null=True)
    eleg_commision = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    policy_status = models.CharField(max_length=45)
    # Dates
    date_birth = models.DateField()
    pol_rec_date = models.DateField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    paid_date = models.DateField(blank=True, null=True)
    term_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "bob_global"


# Others
class AgentInsured(models.Model):
    id_agent = models.IntegerField()
    id_insured = models.IntegerField()

    class Meta:
        managed = False
        db_table = "agent_insured"


class AgentLanguage(models.Model):
    id_agent = models.ForeignKey(
        Agent, models.DO_NOTHING, db_column="id_agent")
    id_language = models.ForeignKey(
        Language, models.DO_NOTHING, db_column="id_language"
    )

    class Meta:
        managed = False
        db_table = "agent_language"


class AgentProduct(models.Model):
    id_agent = models.ForeignKey(
        Agent, models.DO_NOTHING, db_column="id_agent")
    id_product = models.ForeignKey(
        Product, models.DO_NOTHING, db_column="id_product")
    date_certif = models.DateField()
    num_certif = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "agent_product"


class AssitState(models.Model):
    id_asistente = models.IntegerField()
    id_agente = models.IntegerField()
    id_state = models.IntegerField()
    posicion = models.IntegerField()

    class Meta:
        managed = False
        db_table = "assit_state"


class AssitInsurance(models.Model):
    id_asistente = models.IntegerField()
    id_agente = models.IntegerField()
    id_insurance = models.IntegerField()
    posicion = models.IntegerField()

    class Meta:
        managed = False
        db_table = "assit_insurance"


class Claim(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField(blank=True)
    insured = models.ForeignKey(
        Insured,
        models.SET_NULL,
        db_column="id_insured",
        null=True,
        default=None,
        related_name="+",
    )
    # Strings
    names = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    subcriberid = models.CharField(max_length=20, blank=True)
    note = models.TextField(blank=True, null=True)
    note_responce = models.TextField(blank=True)
    # Dates
    # Field name made lowercase.
    efectibedate = models.DateField(db_column="efectibeDate", blank=True)
    date_end = models.DateField(blank=True)
    date_begin = models.DateField(auto_now_add=True, blank=True, null=True)
    # Numbers
    menber_number = models.IntegerField(blank=True, null=True)
    months = models.CharField(max_length=50, blank=True, null=True)
    finished = models.IntegerField(blank=True)
    seen = models.IntegerField(blank=True, null=True)
    # Files
    file = models.FileField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "claim"


class ClientDocument(models.Model):
    id_client = models.IntegerField()
    id_typedocument = models.IntegerField()
    doc_name = models.FileField()
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = "client_document"


class ClientParient(models.Model):
    # ForeignKeys
    id_client = models.IntegerField()
    id_status = models.IntegerField()
    # Strings
    names = models.CharField(max_length=50, blank=True)
    lastnames = models.CharField(max_length=50, blank=True)
    coverrage = models.CharField(max_length=1, blank=True)
    social_security = models.CharField(max_length=15, blank=True)
    alien = models.CharField(max_length=50, blank=True)
    card = models.CharField(max_length=50, blank=True)
    src = models.CharField(max_length=50, blank=True)
    catagory = models.CharField(max_length=50, blank=True)
    folio = models.CharField(max_length=50, blank=True)
    depature = models.CharField(max_length=50, blank=True)
    # Dates
    date_brith = models.DateField(blank=True)
    fechaexdition = models.DateField(blank=True)
    cardexp = models.DateField(blank=True)
    # Numbers
    sexo = models.IntegerField(blank=True)
    pos = models.IntegerField(blank=True)

    class Meta:
        managed = False
        db_table = "client_parient"


class History(models.Model):
    id_client = models.IntegerField()
    id_agent = models.IntegerField(blank=True)
    control = models.CharField(max_length=30, blank=True)
    h_date = models.DateField()
    note = models.TextField()

    class Meta:
        managed = False
        db_table = "history"


class Log(models.Model):
    id_agent = models.IntegerField()
    id_client = models.IntegerField()
    tipo = models.IntegerField()
    dia_hora = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "log"


class MedicareSocial(models.Model):
    id_medicare = models.IntegerField()
    id_soc_service_refe = models.IntegerField()

    class Meta:
        managed = False
        db_table = "medicare_social"


class Menu(models.Model):
    nombre = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    orden = models.IntegerField()
    grupo = models.IntegerField()
    icono = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "menu"


class Payments(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField()
    id_client = models.IntegerField()
    # Strings
    fecha = models.TextField()  # This field type is a guess.
    # Numbers
    january = models.DecimalField(max_digits=12, decimal_places=2)
    february = models.DecimalField(max_digits=12, decimal_places=2)
    march = models.DecimalField(max_digits=12, decimal_places=2)
    april = models.DecimalField(max_digits=12, decimal_places=2)
    may = models.DecimalField(max_digits=12, decimal_places=2)
    june = models.DecimalField(max_digits=12, decimal_places=2)
    july = models.DecimalField(max_digits=12, decimal_places=2)
    august = models.DecimalField(max_digits=12, decimal_places=2)
    september = models.DecimalField(max_digits=12, decimal_places=2)
    october = models.DecimalField(max_digits=12, decimal_places=2)
    november = models.DecimalField(max_digits=12, decimal_places=2)
    dicember = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "payments"


class PaymentsGlobal(models.Model):
    # ForeignKeys
    id_insured = models.IntegerField()
    # Strings
    c_name = models.CharField(max_length=150)
    agent_name = models.CharField(max_length=150, null=True, blank=True)
    p_state = models.CharField(max_length=2, blank=True, null=True)
    p_number = models.CharField(max_length=15)
    month = models.CharField(max_length=2)
    info_month = models.CharField(max_length=10)
    pyear = models.TextField()  # This field type is a guess.
    new_ren = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    # Numbers
    a_number = models.CharField(max_length=50, blank=True, null=True)
    n_member = models.IntegerField()
    rate = models.IntegerField(blank=True, null=True)
    commission = models.FloatField()
    procedado = models.IntegerField()
    # Dates
    e_date = models.DateField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "payments_global"


class PaymentsGlobalTmp(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField()
    id_insured = models.IntegerField()
    # Strings
    c_name = models.CharField(max_length=150)
    p_state = models.CharField(max_length=2, blank=True, null=True)
    p_number = models.CharField(max_length=15)
    month = models.CharField(max_length=2)
    pyear = models.TextField()  # This field type is a guess.
    new_ren = models.CharField(max_length=6, blank=True, null=True)
    month_pay = models.CharField(max_length=15)
    # Numbers
    a_number = models.IntegerField(blank=True, null=True)
    n_member = models.IntegerField()
    rate = models.IntegerField(blank=True, null=True)
    commission = models.FloatField()
    e_date = models.DateField(blank=True, null=True)
    # Dates
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "payments_global_tmp"


class Paymentsagency(models.Model):
    # ForeignKeys
    id_agency = models.IntegerField()
    id_insured = models.IntegerField()
    # Numbers
    procesado = models.IntegerField(blank=True, null=True)
    no_payment = models.IntegerField(blank=True, null=True)
    payment = models.DecimalField(max_digits=12, decimal_places=2)
    num_payment = models.IntegerField()
    # Dates
    month = models.CharField(max_length=2, blank=True, null=True)
    fecha = models.DateField()
    # This field type is a guess.
    year = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "paymentsagency"


class Paymentsasistent(models.Model):
    # ForeingKeys
    id_asistent = models.IntegerField()
    # Strings
    # Numbers
    payment = models.DecimalField(max_digits=12, decimal_places=2)
    num_payment = models.IntegerField()
    id_insured = models.IntegerField()
    procesado = models.IntegerField(blank=True, null=True)
    no_payment = models.IntegerField(blank=True, null=True)
    # Dates
    fecha = models.DateField()
    # This field type is a guess.
    year = models.TextField(blank=True, null=True)
    month = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "paymentsasistent"


class PendingDocuments(models.Model):
    id_client = models.IntegerField()
    id_tipopendoc = models.IntegerField(blank=True, null=True)
    upload_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    nota = models.CharField(
        max_length=255, db_collation="latin1_spanish_ci", blank=True
    )

    class Meta:
        managed = False
        db_table = "pending_documents"


# Temporal Check


class Permisos(models.Model):
    id_usaurio = models.IntegerField()
    id_menu = models.ForeignKey(Menu, models.DO_NOTHING, db_column="id_menu")
    nuevo = models.IntegerField()
    editar = models.IntegerField()
    mostrar = models.IntegerField()
    borrar = models.IntegerField()
    pdf = models.IntegerField()
    excel = models.IntegerField()

    class Meta:
        managed = False
        db_table = "permisos"


class ProstManeger(models.Model):
    # ForeignKeys
    id_product = models.IntegerField()
    id_agent = models.IntegerField()
    idstatus = models.IntegerField()
    # Strings
    name = models.CharField(max_length=50, db_collation="latin1_swedish_ci")
    last_name = models.CharField(
        max_length=100, db_collation="latin1_swedish_ci")
    telephone = models.CharField(
        max_length=50, db_collation="latin1_swedish_ci")
    address = models.CharField(
        max_length=250, db_collation="latin1_swedish_ci")
    email = models.CharField(max_length=150, db_collation="latin1_swedish_ci")
    referred = models.CharField(
        max_length=50, db_collation="latin1_swedish_ci")
    # Dates
    date_brith = models.DateField()

    class Meta:
        managed = False
        db_table = "prost_maneger"


class RegistreAsis(models.Model):
    id_asistente = models.IntegerField()
    fecha = models.DateField()
    hora_ent = models.TimeField()
    hora_sal = models.TimeField()

    class Meta:
        managed = False
        db_table = "registre_asis"


class Registro(models.Model):
    # ForeignKeys
    id_incured = models.IntegerField()
    # Strings
    subcriberid = models.CharField(max_length=15)
    # Field renamed because it was a Python reserved word.
    class_field = models.CharField(db_column="class", max_length=10)
    state = models.CharField(max_length=3)
    # Numbers
    npn = models.IntegerField()
    member = models.IntegerField()
    com_paym = models.DecimalField(max_digits=12, decimal_places=2)
    # Dates
    effectivedate = models.CharField(max_length=20)
    month = models.CharField(max_length=20)
    fecha = models.DateField()
    procedado = models.IntegerField()

    class Meta:
        managed = False
        db_table = "registro"


class Table5(models.Model):
    names = models.CharField(max_length=150)
    policynumber = models.CharField(max_length=10)
    fields = models.JSONField(null=True)

    class Meta:
        managed = False
        db_table = "table5"


# Table for keeping records of extrafields added to the Tables
class ExtraFields(models.Model):
    table_name = models.CharField(max_length=50)
    field_name = models.CharField(max_length=100)
    # required=models.BooleanField(default=False)
    # data_type=models.CharField(max_length=50)


class PaymentsControl(models.Model):
    index_payment = models.IntegerField()
    id_payment = models.IntegerField()
    id_insured = models.IntegerField()
    id_agent = models.IntegerField()
    month = models.CharField(max_length=15)
    year_made = models.CharField(max_length=4)
    commision = models.FloatField()
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = "payments_control"


class PaymentsGlobalAgency(models.Model):
    # ForeignKeys
    agent = models.ForeignKey(
        Agent, on_delete=models.DO_NOTHING, db_column="id_agent"
    )  # id_agent = models.IntegerField()
    client = models.ForeignKey(
        Client, on_delete=models.DO_NOTHING, db_column="id_client"
    )  # id_client = models.IntegerField()
    insured = models.ForeignKey(
        Insured, on_delete=models.DO_NOTHING, db_column="id_insured"
    )  # id_insured = models.IntegerField()
    agency = models.ForeignKey(
        Agency, on_delete=models.DO_NOTHING, db_column="id_agency"
    )  # id_agency = models.IntegerField()
    sec_pay_from_insured = models.IntegerField(null=True, default=None)
    # Strings
    year = models.CharField(max_length=4, blank=True)
    month = models.CharField(max_length=15, blank=True)
    info_month = models.CharField(max_length=15, blank=True)
    repaid_on = models.CharField(max_length=15, blank=True, null=True)
    # Numbers
    members_number = models.IntegerField()
    indx = models.IntegerField()
    total_commission = models.FloatField()
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = False
        db_table = "payments_global_agency"


class AgencyRepayments(models.Model):
    # ForeignKeys
    agent = models.ForeignKey(
        Agent, on_delete=models.DO_NOTHING, db_column="id_agent"
    )  # id_agent = models.IntegerField()
    client = models.ForeignKey(
        Client, on_delete=models.DO_NOTHING, db_column="id_client"
    )  # id_client = models.IntegerField()
    insured = models.ForeignKey(
        Insured, on_delete=models.DO_NOTHING, db_column="id_insured"
    )  # id_insured = models.IntegerField()
    agency = models.ForeignKey(
        Agency, on_delete=models.DO_NOTHING, db_column="id_agency"
    )  # id_agency = models.IntegerField()
    sec_pay_from_insured = models.IntegerField(null=True, default=None)
    # Strings
    year = models.CharField(max_length=4, blank=True)
    month = models.CharField(max_length=15, blank=True)
    info_month = models.CharField(max_length=15, blank=True)
    # Numbers
    members_number = models.IntegerField()
    indx = models.IntegerField()
    total_commission = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = False
        db_table = "agency_repayment"


class PaymentsGlobalAssistant(models.Model):
    # ForeignKeys
    id_agent = models.IntegerField()
    id_client = models.IntegerField()
    id_insured = models.IntegerField()
    id_assistant = models.IntegerField()
    id_state = models.IntegerField()
    # Strings
    year = models.CharField(max_length=4, blank=True)
    month = models.CharField(max_length=15, blank=True)
    # Numbers
    members_number = models.IntegerField()
    indx = models.IntegerField()
    total_commission = models.FloatField()

    class Meta:
        managed = False
        db_table = "payments_global_assistant"


class AgentCommission(models.Model):
    # ForeignKeys
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        db_column="id_agent",
        related_name="commissions",
    )
    insured = models.ForeignKey(
        Insured,
        on_delete=models.CASCADE,
        db_column="id_insured",
        related_name="+",
    )
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        db_column="id_state",
        related_name="+",
    )
    # Numbers
    comm_new = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    comm_rew = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    comm_set = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    comm_set2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    # Strings
    yearcom = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = "agent_commission"
        constraints = [
            models.UniqueConstraint(
                fields=["insured", "state", "agent", "yearcom"],
                name="AgentComm C1",
            )
        ]


class GroupCommission(models.Model):
    group = models.ForeignKey(
        CommissionsGroup,
        on_delete=models.CASCADE,
        db_column="id_group",
        related_name="commissions",
    )
    insured = models.ForeignKey(
        Insured,
        on_delete=models.CASCADE,
        db_column="id_insured",
        related_name="+",
    )
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        db_column="id_state",
        related_name="+",
    )
    # Numbers
    comm_new = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    comm_rew = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    comm_set = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    comm_set2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0
    )
    # Strings
    yearcom = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = "group_commission"
        constraints = [
            models.UniqueConstraint(
                fields=["insured", "state", "group", "yearcom"],
                name="GroupComm C1",
            )
        ]


class ApiLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    added_on = models.DateTimeField(auto_now_add=True)
    api = models.CharField(max_length=1024, help_text="API URL")
    headers = models.TextField()
    body = models.TextField()
    method = models.CharField(max_length=10, db_index=True)
    client_ip_address = models.CharField(max_length=50)
    response = models.TextField()
    status_code = models.PositiveSmallIntegerField(
        help_text="Response status code", db_index=True
    )
    execution_time = models.DecimalField(
        decimal_places=5,
        max_digits=8,
        help_text="Server execution time (Not complete response time.)",
    )
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    user_email = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "api_logs"


class EmptyPaymentLogEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    suscriberid = models.TextField(blank=True, null=True)
    bob_id = models.TextField(blank=True, null=True)
    client_id = models.IntegerField(null=True)
    client_name = models.TextField(blank=True, null=True)
    member_number = models.TextField(blank=True, null=True)
    info_month = models.TextField(blank=True, null=True)
    agent_id = models.IntegerField(null=True)
    agent_npn = models.TextField(blank=True, null=True)
    agent_name = models.TextField(blank=True, null=True)
    agent_year_comm = models.FloatField(blank=True, null=True)
    insured_id = models.IntegerField(null=True)
    insured_name = models.TextField(blank=True, null=True)
    state_id = models.IntegerField(null=True)
    state_sigla = models.TextField(blank=True, null=True)
    payment_type = models.TextField(blank=True, null=True)
    payment_total = models.FloatField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    payment_year = models.TextField()
    payment_month = models.TextField()
    repayment = models.BooleanField()
    added_on = models.DateTimeField(auto_now_add=True)
    payment_id = models.IntegerField(null=True)

    class Meta:
        db_table = "zero_payment_logs"


class ClientLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    added_on = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)
    description = models.CharField(
        max_length=4000, null=True, default=None, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "client_log"
        managed = False


class AgentPortal(models.Model):
    id = models.BigAutoField(primary_key=True)
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, null=True, blank=True)
    insured = models.ForeignKey(
        Insured, on_delete=models.CASCADE, null=True, blank=True)
    user = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    question1 = models.CharField(max_length=500, null=True, blank=True)
    answer1 = models.CharField(max_length=500, null=True, blank=True)
    question2 = models.CharField(max_length=500, null=True, blank=True)
    answer2 = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "agent_portal"
        managed = False


class PaymentExcel(models.Model):
    id = models.BigAutoField(primary_key=True)
    insured = models.IntegerField(null=True, blank=True)
    month = models.CharField(max_length=20, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    file = models.FileField(blank=True, null=True)

    class Meta:
        db_table = "payment_excel"
        managed = False


class OriginalPayment(models.Model):
    id = models.BigAutoField(primary_key=True)
    insured = models.IntegerField(null=True, blank=True)
    agent = models.IntegerField(null=True, blank=True)
    client_name = models.CharField(max_length=200, null=True, blank=True)
    suscriber_id = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    npn = models.CharField(max_length=20, null=True, blank=True)
    member_number = models.IntegerField(null=True, blank=True)
    effective_date = models.DateField(blank=True, null=True)
    info_month = models.CharField(max_length=10, blank=True, null=True)
    commission = models.FloatField(null=True, blank=True)
    new_ren = models.CharField(max_length=20, null=True, blank=True)
    month = models.CharField(max_length=10, null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        db_table = "original_payment"
        managed = False


class USZips(models.Model):
    id = models.BigAutoField(primary_key=True)
    zip = models.CharField(max_length=5, null=True, blank=True)
    city = models.CharField(max_length=27, null=True, blank=True)
    state_id = models.CharField(max_length=2, null=True, blank=True)
    state_name = models.CharField(max_length=24, null=True, blank=True)
    county_fips = models.CharField(max_length=5, null=True, blank=True)
    county_name = models.CharField(max_length=21, null=True, blank=True)
    county_names_all = models.CharField(max_length=63, null=True, blank=True)
    county_fips_all = models.CharField(max_length=35, null=True, blank=True)

    class Meta:
        db_table = "uszips"
        managed = False


class AgentPayments(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ForeignKeys
    id_agent = models.IntegerField()
    id_client = models.IntegerField()
    id_insured = models.IntegerField()
    id_state = models.IntegerField()
    # Strings
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=15)
    info_month = models.CharField(max_length=15)
    payment_type = models.CharField(max_length=15)
    agent_name = models.CharField(max_length=200, blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    insured_name = models.CharField(max_length=200, blank=True)
    suscriberid = models.CharField(max_length=50)
    repaid_on = models.CharField(max_length=15, null=True, default=None)
    description = models.CharField(max_length=500, blank=True, null=True)
    # Numbers
    members_number = models.IntegerField()
    payment_index = models.IntegerField()
    commission = models.FloatField()
    # Dates
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = "agent_payments"
        managed = False


class Repayments(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ForeignKeys
    id_agent = models.IntegerField()
    id_client = models.IntegerField()
    id_insured = models.IntegerField()
    id_state = models.IntegerField()
    # Strings
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=15)
    info_month = models.CharField(max_length=15)
    payment_type = models.CharField(max_length=15)
    agent_name = models.CharField(max_length=200, blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    insured_name = models.CharField(max_length=200, blank=True)
    suscriberid = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    # Numbers
    members_number = models.IntegerField()
    payment_index = models.IntegerField()
    commission = models.FloatField()
    original_commission = models.FloatField(null=True)
    # Dates
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = "repayments"
        managed = False


class FuturePayments(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ForeignKeys
    id_agent = models.IntegerField()
    id_client = models.IntegerField()
    id_insured = models.IntegerField()
    id_state = models.IntegerField()
    # Strings
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=15)
    info_month = models.CharField(max_length=15)
    payment_type = models.CharField(max_length=15)
    agent_name = models.CharField(max_length=200, blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    insured_name = models.CharField(max_length=200, blank=True)
    suscriberid = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    # Numbers
    members_number = models.IntegerField()
    payment_index = models.IntegerField()
    commission = models.FloatField()
    original_commission = models.FloatField(null=True)
    # Dates
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = "future_payments"
        managed = False


class ClaimHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_claim = models.IntegerField()
    claimer = models.BooleanField()
    seen = models.BooleanField(default=False)
    message = models.CharField(max_length=2000)
    message_number = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    file = models.FileField(blank=True, null=True)

    class Meta:
        db_table = 'claim_history'
        managed = False


class SubscriberIdTemplate(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_insured = models.IntegerField(unique=True)
    example = models.CharField(max_length=50)

    class Meta:
        db_table = 'sub_id_template'
        managed = False


class ClientConsentLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_client = models.IntegerField()
    id_agent = models.IntegerField()
    client_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    sended = models.BooleanField(null=True, default=None)
    signed = models.BooleanField(null=True, default=None)
    year = models.CharField(max_length=4)

    deductible = models.FloatField(null=True)
    max_out_pocket = models.FloatField(null=True)
    plan_name = models.CharField(max_length=255, null=True)
    monthly_payment = models.FloatField(null=True)
    principal_income = models.FloatField(null=True)
    client_dob = models.CharField(max_length=15, null=True)
    lan = models.CharField(max_length=2, null=True)
    client_tel = models.CharField(max_length=20, null=True)
    client_email = models.CharField(max_length=50, null=True)
    main_agent_npn = models.CharField(max_length=15, null=True)
    main_agent_tel = models.CharField(max_length=15, null=True)
    main_agent_name = models.CharField(max_length=100, null=True)
    secondary_agent_npn = models.CharField(max_length=15, null=True)
    secondary_agent_tel = models.CharField(max_length=15, null=True)
    secondary_agent_name = models.CharField(max_length=100, null=True)
    secret_key = models.CharField(max_length=100, null=True)
    update_type = models.CharField(max_length=100, null=True)
    effective_date = models.CharField(max_length=100, null=True)

    date_sended = models.DateTimeField(
        blank=True, null=True)
    date_signed = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'client_consent_log'
        managed = False


class AgentGlobalCE(models.Model):
    id = models.BigAutoField(primary_key=True)
    npn = models.CharField(max_length=30, null=False, blank=False)

    ce_due_date = models.CharField(max_length=50, null=True)
    ce_req_hours = models.CharField(max_length=50, null=True)
    ce_completed_hours = models.CharField(
        max_length=50, null=True)

    class Meta:
        managed = False
        db_table = "agent_global_ce"


class AgentGlobalAppointments(models.Model):
    id = models.BigAutoField(primary_key=True)
    npn = models.CharField(max_length=30, null=False, blank=False)
    license_num = models.CharField(max_length=30)
    agent_name = models.CharField(max_length=300)
    business_address = models.CharField(
        max_length=1000)
    mailing_address = models.CharField(
        max_length=1000)
    county = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    company_name = models.CharField(max_length=200)
    issue_date = models.CharField(max_length=50)
    exp_date = models.CharField(max_length=50)
    app_type = models.CharField(max_length=100)
    app_code = models.CharField(max_length=50)
    active_or_not = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "agent_global_appointment"


class AgentGlobalLicenses(models.Model):
    id = models.BigAutoField(primary_key=True)
    npn = models.CharField(max_length=30, null=False, blank=False)
    license_type = models.CharField(
        max_length=100, null=True)
    license_issue_date = models.CharField(
        max_length=50, null=True)
    license_code = models.CharField(
        max_length=50, null=True)
    license_active_or_not = models.BooleanField(default=False, null=True)

    class Meta:
        managed = False
        db_table = "agent_global_license"


class Override(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ForeignKeys
    id_insured = models.IntegerField()
    # Strings
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=15)
    state = models.CharField(max_length=15)
    info_month = models.CharField(max_length=15)
    payment_type = models.CharField(max_length=15)
    client_name = models.CharField(max_length=200, blank=True)
    agent_name = models.CharField(max_length=200, blank=True, null=True)
    insured_name = models.CharField(max_length=200, blank=True)
    suscriberid = models.CharField(max_length=50)
    # Numbers
    members_number = models.IntegerField()
    commission = models.FloatField()
    # Dates
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = "override"
        managed = False


class ClientMedicaid(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ForeignKeys
    id_agent = models.IntegerField(null=True, blank=True)
    id_status = models.IntegerField(null=True, blank=True)
    # Strings
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    access_user = models.CharField(max_length=50, null=True, blank=True)
    access_password = models.CharField(max_length=50, null=True, blank=True)
    ssn = models.CharField(max_length=9, null=True, blank=True)
    income_source = models.CharField(max_length=4, null=True, blank=True)
    employer_name = models.CharField(max_length=100, null=True, blank=True)
    employer_telephone = models.CharField(
        max_length=100, null=True, blank=True)
    alien = models.CharField(max_length=20, null=True, blank=True)
    birth_country = models.CharField(max_length=100, null=True, blank=True)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    # Numbers
    income = models.FloatField(null=True)
    # Booleans
    approval = models.BooleanField(default=False)
    medicare = models.BooleanField(default=False)
    obamacare = models.BooleanField(default=False)
    # Dates
    dob = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)
    application_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "client_medicaid"
        managed = False


class UnAssignedPayments(models.Model):
    id_insured = models.IntegerField(null=True)
    # Strings
    client_name = models.CharField(max_length=150, null=True)
    agent_name = models.CharField(max_length=150, null=True)
    state_initials = models.CharField(max_length=2, blank=True, null=True)
    suscriberid = models.CharField(max_length=15, null=True)
    month = models.CharField(max_length=2, null=True)
    info_month = models.CharField(max_length=10, null=True)
    year = models.TextField(null=True)  # This field type is a guess.
    new_ren = models.CharField(max_length=10, blank=True, null=True)
    # Numbers
    npn = models.IntegerField(blank=True, null=True)
    members = models.IntegerField(null=True)
    rate = models.IntegerField(blank=True, null=True)
    commission = models.FloatField(null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    # Dates
    effective_date = models.DateField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "unassigned_payments"
        managed = False


class SecondaryOverride(models.Model):
    id_insured = models.ForeignKey(
        Insured,
        on_delete=models.SET_NULL,
        db_column="id_insured",
        related_name="secondary_overrides",
        null=True,
    )
    id_parent_agency = models.ForeignKey(
        Agency,
        on_delete=models.SET_NULL,
        db_column="id_parent_agency",
        related_name="secondary_overrides",
        null=True,
    )
    id_children_agency = models.ForeignKey(
        Agency,
        on_delete=models.SET_NULL,
        db_column="id_children_agency",
        null=True,
    )
    amount_per_member = models.FloatField(null=True)

    class Meta:
        db_table = "secondary_override"
        managed = False


class IncomeLetterLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_client = models.IntegerField()
    id_agent = models.IntegerField()
    client_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    sended = models.BooleanField(null=True, default=None)
    signed = models.BooleanField(null=True, default=None)
    year = models.CharField(max_length=4)

    application_id = models.CharField(max_length=30, null=True)
    ssn = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=300, null=True)
    client_dob = models.CharField(max_length=15, null=True)
    income = models.FloatField(null=True)
    client_tel = models.CharField(max_length=20, null=True)

    lan = models.CharField(max_length=2, null=True)
    secret_key = models.CharField(max_length=100, null=True)

    date_sended = models.DateTimeField(
        blank=True, null=True)
    date_signed = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'income_letter_log'
        managed = False


class PreLetterLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_agent = models.IntegerField()
    client_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    sended = models.BooleanField(null=True, default=None)
    signed = models.BooleanField(null=True, default=None)
    year = models.CharField(max_length=4)

    agent_name = models.CharField(max_length=100, null=True)
    agent_npn = models.CharField(max_length=30, null=True)
    agent_phone = models.CharField(max_length=30, null=True)
    client_dob = models.CharField(max_length=15, null=True)
    client_tel = models.CharField(max_length=20, null=True)
    client_email = models.CharField(max_length=20, null=True)

    lan = models.CharField(max_length=2, null=True)
    secret_key = models.CharField(max_length=100, null=True)

    date_sended = models.DateTimeField(
        blank=True, null=True)
    date_signed = models.DateTimeField(blank=True, null=True)

    file = models.FileField(null=True)

    class Meta:
        db_table = 'pre_letter_log'
        managed = False


class PDFNotice(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    file = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdf_notices'
        managed = False


class ApplicationProblem(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_client = models.IntegerField()
    id_problem = models.IntegerField()

    class Meta:
        db_table = 'application_problems'
        managed = False


class Problem(models.Model):
    id = models.BigAutoField(primary_key=True)
    names = models.CharField(max_length=100)

    class Meta:
        db_table = 'problems'
        managed = False

# class SelfManagedAgencyPayment(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     # ForeignKeys
#     id_agent = models.IntegerField()
#     id_client = models.IntegerField()
#     id_insured = models.IntegerField()
#     id_state = models.IntegerField()
#     id_agency = models.IntegerField()
#     # Strings
#     year = models.CharField(max_length=4)
#     month = models.CharField(max_length=15)
#     info_month = models.CharField(max_length=15)
#     payment_type = models.CharField(max_length=15)
#     agent_name = models.CharField(max_length=200, blank=True)
#     client_name = models.CharField(max_length=200, blank=True)
#     insured_name = models.CharField(max_length=200, blank=True)
#     agency_name = models.CharField(max_length=200, blank=True)
#     suscriberid = models.CharField(max_length=50)
#     # Numbers
#     members_number = models.IntegerField()
#     commission = models.FloatField()
#     # Dates
#     created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

#     class Meta:
#         db_table = "self_managed_agency_payment"
#         managed = False
