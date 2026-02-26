import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# 1. Load the dataset
df = pd.read_csv('dataset.csv')

# 2. Convert text to numbers (TF-IDF)
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['label']

# 3. Train the model
model = LogisticRegression()
model.fit(X, y)

# 4. Save the model and vectorizer to use in your Flutter backend
joblib.dump(model, 'cyber_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("Model trained and saved successfully!")