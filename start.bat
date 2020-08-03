python ./CreateCSV.py
python ./Analyse.py
cd output_final
ipython nbconvert --to HTML analysis.ipynb
