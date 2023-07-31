import pandas as pd
import numpy as np
import seaborn as sns

politics = pd.read_csv('../Data/Dataset/politics.csv')
cultur = pd.read_csv('../Data/Dataset/cultur.csv')
economy = pd.read_csv('../Data/Dataset/economy.csv')
eduction = pd.read_csv('../Data/Dataset/education.csv')
sport = pd.read_csv('../Data/Dataset/sport.csv')
df = pd.concat([politics, cultur, economy, eduction, sport])
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
# Transformers
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

Xfeatures = df['Text']
ylabels = df['Title']
x_train, x_test, y_train, y_test = train_test_split(Xfeatures, ylabels, test_size=0.3, random_state=42)
pipe_lr = Pipeline(steps=[('cv', CountVectorizer()), ('lr', LogisticRegression())])
pipe_lr.fit(x_train, y_train)


def TopicModeling(Text):
    WordCnt = Text.split(' ')
    if len(WordCnt) >= 5:
        Topic = pipe_lr.predict([Text])[0]
        return Topic
    else:
        return 'Short Text'
