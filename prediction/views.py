from django.shortcuts import render
from .forms import PredictionForm, CSVUploadForm
from .utils import predict_from_data
import pandas as pd
import io

def index(request):
    form = PredictionForm()
    csv_form = CSVUploadForm()
    return render(request, 'prediction/index.html', {'form': form, 'csv_form': csv_form})


def predict_manual(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            from .utils import load_artifacts
            _, _, selected_cols = load_artifacts()
            # Construire le DataFrame avec l'ordre exact des colonnes
            data = {col: [form.cleaned_data[col]] for col in selected_cols}
            df = pd.DataFrame(data)
            y_pred, y_proba = predict_from_data(df)
            if y_pred is not None:
                classe = "Rouille (rust)" if y_pred[0] == 1 else "Sain (norust)"
                proba = float(y_proba[0])
                return render(request, 'prediction/result.html', {
                    'classe': classe,
                    'probabilite': proba,
                    'is_rust': y_pred[0] == 1
                })
    return render(request, 'prediction/error.html', {'message': 'Erreur de prédiction'})


def predict_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['csv_file']
            file_name = uploaded_file.name.lower()
            try:
                # Lecture du fichier (CSV ou Excel)
                if file_name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    content = uploaded_file.read()
                    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
                    decoded = None
                    for enc in encodings:
                        try:
                            decoded = content.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    if decoded is None:
                        raise ValueError("Encodage non reconnu")
                    df = pd.read_csv(io.StringIO(decoded))

                from .utils import load_artifacts
                model, scaler, selected_cols = load_artifacts()
                missing = set(selected_cols) - set(df.columns)
                if missing:
                    return render(request, 'prediction/error.html',
                                  {'message': f'Colonnes manquantes : {missing}'})
                df_valid = df[selected_cols].dropna()
                if df_valid.empty:
                    return render(request, 'prediction/error.html',
                                  {'message': 'Aucune ligne valide'})
                X_scaled = scaler.transform(df_valid)
                y_pred = model.predict(X_scaled)
                y_proba = model.predict_proba(X_scaled)[:, 1]
                df_result = df_valid.copy()
                df_result['prediction'] = y_pred
                df_result['probabilite_rust'] = y_proba

                # --- Modification : remplacer 0/1 par des badges colorés ---
                def format_prediction(val):
                    if val == 1:
                        return '<span class="badge-rust">rust</span>'
                    else:
                        return '<span class="badge-norust">norust</span>'

                # Appliquer le formatage sur la colonne 'prediction'
                df_result['prediction'] = df_result['prediction'].apply(format_prediction)
                # Arrondir la probabilité pour un affichage plus propre
                df_result['probabilite_rust'] = df_result['probabilite_rust'].apply(lambda x: f"{x:.4f}")

                # Générer le tableau HTML sans échappement (escape=False)
                table_html = df_result.to_html(classes='table-predictions', escape=False, index=False)

                return render(request, 'prediction/upload_result.html', {'table': table_html})
            except Exception as e:
                return render(request, 'prediction/error.html', {'message': str(e)})
    return render(request, 'prediction/error.html', {'message': 'Méthode non autorisée'})

def model_info(request):
    # Valeurs obtenues lors de l'évaluation (à adapter)
    confusion_matrix = [[194, 75], [0, 801]]   # [norust, rust] depuis validation croisée
    accuracy = 0.9299
    f1 = 0.9258
    # Récupérer les noms des colonnes sélectionnées
    from .utils import load_artifacts
    _, _, selected = load_artifacts()
    return render(request, 'prediction/model_info.html', {
        'confusion_matrix': confusion_matrix,
        'accuracy': accuracy,
        'f1_score': f1,
        'selected_features': selected
    })