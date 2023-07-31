from django.utils.translation import gettext_lazy as _


ERROR_MESSAGES = {
    "unique_field": _("This field should be unique."),
    "not_period_member": _("Persons should be a member of this period first."),
    "required_field": _("This field is required."),
    "permission_denied": _('You do not have permission to perform this action.')

}

RESPONSE_MESSAGES = {
    "successfully_deleted": _("Deleted Successfully")
}
