from london.dispatch import Signal
from images import add_image_field_to_sender_form
from london.apps.seo import add_meta_info_fields_to_sender_form, save_meta_info_from_sender_form

post_form_initialize = Signal()
post_form_initialize.connect(add_meta_info_fields_to_sender_form)
post_form_initialize.connect(add_image_field_to_sender_form)
post_form_pre_save = Signal()
post_form_post_save = Signal()
post_form_post_save.connect(save_meta_info_from_sender_form)
#post_form_clean = Signal()