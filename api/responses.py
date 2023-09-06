from django.utils.translation import gettext_lazy as _

ERROR_MESSAGES = {
    "unique_field": _("This field should be unique."),
    "not_period_member": _("Persons should be a member of this period first."),
    "required_field": _("This field is required."),
    "permission_denied": _("You do not have permission to perform this action."),
    "person_object_protected": _(
        "you cant remove these persons, some of the persons are part of purchases. try deleting person from that purchases and try again."
    ),
    "already_exists": _(
        "user with this email or username is already exists, try another one."
    ),
    "period_limit_reached": _(
        "You have reached maximum amount of period creation, delete some period to make new periods."
    ),
    "code_argument_missing": _("required url argument 'code' is missing"),
    "invalid_refresh_token": _("refresh_token is not valid"),
    "expired_token": _("The Token is expired, ask for another one"),
    "login_link_timeout": _("You asked for a login link recently, Please wait after you can get new one!"),

}

RESPONSE_MESSAGES = {
    "successfully_deleted": _("Deleted Successfully"),
    "logged_out": _("logged out"),
    "magic_link_sent": _("magic link has been sent to your email"),
}
