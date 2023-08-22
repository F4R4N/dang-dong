from django.utils.translation import gettext_lazy as _


ERROR_MESSAGES = {
    "unique_field": _("This field should be unique."),
    "not_period_member": _("Persons should be a member of this period first."),
    "required_field": _("This field is required."),
    "permission_denied": _('You do not have permission to perform this action.'),
    "person_object_protected": _("you cant remove these persons, some of the persons are part of purchases. try deleting person from that purchases and try again."),
    "already_exists": _("user with this email or username is already exists, try another one.")

}

RESPONSE_MESSAGES = {
    "successfully_deleted": _("Deleted Successfully")
}
