from django.utils.translation import gettext_lazy as _


ERROR_MESSAGES = {
    "unique_field": _("This field should be unique"),
    "not_period_member": _("Persons should be a member of this period first.")
}

RESPONSE_MESSAGES = {
    "successfully_deleted": _("Deleted Successfully")
}
