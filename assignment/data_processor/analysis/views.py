from django.shortcuts import render, redirect
from .forms import CSVUploadForm
from .models import CSVFile
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

def handle_uploaded_file(file):
    file_path = os.path.join('media/csvs', file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path

def upload_file(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.save()
            file_path = handle_uploaded_file(request.FILES['file'])
            data = pd.read_csv(file_path)
            
            # Perform data analysis using pandas and numpy
            first_rows = data.head().to_html()
            summary_statistics = data.describe().to_html()
            missing_values = data.isnull().sum().to_frame(name='Missing Values').to_html()
            
            # Check for numerical columns before plotting
            numerical_columns = data.select_dtypes(include=[np.number]).columns
            plot_urls = []
            if len(numerical_columns) > 0:
                for column in numerical_columns:
                    plt.figure()
                    sns.histplot(data[column].dropna(), kde=True)
                    plot_path = os.path.join('media', f'plot_{column}.png')
                    plt.savefig(plot_path)
                    plt.close()
                    plot_urls.append(f'/media/plot_{column}.png')

            context = {
                'first_rows': first_rows,
                'summary_statistics': summary_statistics,
                'missing_values': missing_values,
                'plot_urls': plot_urls,
            }
            return render(request, 'analysis/result.html', context)
    else:
        form = CSVUploadForm()
    return render(request, 'analysis/upload.html', {'form': form})
