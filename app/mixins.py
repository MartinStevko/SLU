from django.forms import model_to_dict


class OverwriteOnlyModelFormMixin(object):

    def clean(self):
        cleaned_data = super(OverwriteOnlyModelFormMixin, self).clean()
        c_cl_data = cleaned_data.copy()
        for field in c_cl_data.keys():
            if self.prefix is not None:
                post_key = '-'.join((self.prefix, field))
            else:
                post_key = field

            if post_key not in list(self.data.keys()) + list(self.files.keys()):
                # value was not posted, thus it should not overwrite any data.
                del cleaned_data[field]

        # only overwrite keys that were actually submitted via POST.
        model_data = model_to_dict(self.instance)
        model_data.update(cleaned_data)
        return model_data
