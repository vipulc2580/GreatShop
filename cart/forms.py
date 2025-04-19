from django import forms
from django.core.exceptions import ValidationError
import csv


class CouponForm(forms.Form):
    csv_file = forms.FileField(required=True)
    email_subject = forms.CharField(max_length=255, required=True)
    code = forms.CharField(max_length=20, required=True)
    discount = forms.IntegerField(min_value=1, max_value=60, required=True)
    validity_days = forms.IntegerField(required=True, min_value=1)

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')

        # Check file extension
        if not file.name.endswith('.csv'):
            raise ValidationError("Uploaded file must be a .csv")

        # Check content (structure)
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            rows = list(reader)

            if not rows:
                raise ValidationError("CSV file is empty.")

            # Optional: Check header or number of columns
            # Example: Expecting 1 column with User IDs
            for i, row in enumerate(rows):
                if len(row) != 1:
                    raise ValidationError(
                        f"Row {i+1} is malformed. Expected 1 column, got {len(row)}.")

        except Exception as e:
            raise ValidationError(f"Error processing CSV file: {str(e)}")

        # Rewind the file pointer so it's readable again after validation
        file.seek(0)

        return file
