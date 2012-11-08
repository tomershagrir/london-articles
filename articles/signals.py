from london.dispatch import Signal
from images import add_image_field_to_sender_form
from london.apps.seo import add_meta_info_fields_to_sender_form, save_meta_info_from_sender_form
from london.apps.collections import add_collections_to_sender_form, save_collections_from_sender_form

try:
    from revision import add_delayed_publication_field_to_form, save_delayed_publication
except:
    add_delayed_publication_field_to_form = None
    save_delayed_publication = None

post_form_initialize = Signal()
post_form_initialize.connect(add_meta_info_fields_to_sender_form)
post_form_initialize.connect(add_image_field_to_sender_form)
post_form_initialize.connect(add_collections_to_sender_form)
post_form_pre_save = Signal()
post_form_post_save = Signal()
post_form_post_save.connect(save_meta_info_from_sender_form)
post_form_post_save.connect(save_collections_from_sender_form)
#post_form_clean = Signal()

if add_delayed_publication_field_to_form:
    post_form_initialize.connect(add_delayed_publication_field_to_form)

if save_delayed_publication:
    post_form_post_save.connect(save_delayed_publication)