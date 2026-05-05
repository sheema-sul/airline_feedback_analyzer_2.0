import pandas as pd
import re
import nltk
import pickle

from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# LOAD DATA
data = pd.read_csv("Tweets.csv")

# PREPROCESSING
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

data['clean_text'] = data['text'].apply(preprocess_text)

# TOKENIZATION
MAX_LEN = 100 

tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
tokenizer.fit_on_texts(data['clean_text'])

sequences = tokenizer.texts_to_sequences(data['clean_text'])
padded_sequences = pad_sequences(sequences, maxlen=MAX_LEN, padding='post')

# Labels
labels = pd.get_dummies(data['airline_sentiment']).values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    padded_sequences, labels, test_size=0.2, random_state=42
)

# MODEL
model = Sequential([
    Embedding(input_dim=10000, output_dim=64, input_length=MAX_LEN),
    LSTM(32),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

# TRAIN
model.fit(
    X_train, y_train,
    epochs=3,            # reduced from 5
    batch_size=64,       # increased (faster)
    validation_data=(X_test, y_test)
)

# EVALUATE
loss, acc = model.evaluate(X_test, y_test)
print(f"Accuracy: {acc:.2f}")

# SAVE
model.save("model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("Model and tokenizer saved successfully!")