from django import forms

class PredictionForm(forms.Form):
    Blue_mean = forms.FloatField(label='Blue_mean', required=True)
    Green_mean = forms.FloatField(label='Green_mean', required=True)
    Red_mean = forms.FloatField(label='Red_mean', required=True)
    RedEdge_mean = forms.FloatField(label='RedEdge_mean', required=True)
    NIR_mean = forms.FloatField(label='NIR_mean', required=True)
    GNDVI_std = forms.FloatField(label='GNDVI_std', required=True)
    NDRE_std = forms.FloatField(label='NDRE_std', required=True)
    PSRI_mean = forms.FloatField(label='PSRI_mean', required=True)
    PSRI_std = forms.FloatField(label='PSRI_std', required=True)
    R_B_ratio_mean = forms.FloatField(label='R_B_ratio_mean', required=True)

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Fichier CSV (.csv)', required=True)