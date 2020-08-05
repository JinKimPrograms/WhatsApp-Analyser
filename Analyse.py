
# Handles the analysis of the created CSV - creating figures and dataframes which can be accessed.
import nbformat as nbf
import pandas as pd
import matplotlib.pyplot as plt
import string
from collections import Counter

# line-saving function to label and save graphs
def nameAndSave(graph, x, y, title, fig_number):
    graph.set_xlabel(x)
    graph.set_ylabel(y)
    graph.set_title(title)
    figure = plt.gcf()
    figure.savefig('images/fig' + str(fig_number) + ".png", bbox_inches = 'tight')


# Read dataframe as csv
csv = pd.read_csv("csv_output/dataframe.csv")

# Data cleaning - drop messages with null authors
null_authors_df = csv[csv['Author'].isnull()]
data = csv.drop(null_authors_df.index) # Drops all rows of the data frame containing messages from null authors

# Add additional columns - for looking at the letter/word count and individual words said in message
data['Letter_Count'] = data['Message'].str.len()
data['Words'] = data['Message'].str.split(" ")
data["Word_Count"] = ""
data["Word_Count"][:] = [(len(lst) if isinstance(lst,list) else 0) for lst in data["Words"]]

# Create and save graph for who has sent the most MEDIA (picture, audio, video) mesages)
media_messages_df = data[data['Message'] == "<Media omitted>"]
author_media_messages_value_counts = media_messages_df['Author'].value_counts()
top_10_author_media_messages_value_counts = author_media_messages_value_counts.head(20)
nameAndSave(top_10_author_media_messages_value_counts.plot.barh(), 'Media Messages Sent', 'Author',
            "Who sent the most media (pictures/audio/video) messages?", 1)

# Who has sent the most messages?
author_value_counts = data['Author'].value_counts()
nameAndSave(author_value_counts.plot.barh(), 'Messages Sent', 'Author', 'Who sent the most messages?', 2)

# Days with the most text messages sent
nameAndSave(data['Date'].value_counts().head(10).plot.barh(), "Number of Messages", "Date",
            "Days with the most Text Messages", 5)

# Hours with the most text messages sent
data['Hour'] = data['Time'].apply(lambda x : x.split(":")[0] + x.split(" ")[1])
nameAndSave(data['Hour'].value_counts().head(10).plot.barh(), "Number of Messages", "Hour Sent",
            "When do we usually talk?", 6)

# Who has sent the most words in the group chat?
total_word_count_grouped_by_author = data[['Author', 'Word_Count']].groupby('Author').sum()
word_count_grouped_by_author = total_word_count_grouped_by_author.sort_values('Word_Count', ascending=False)
top_10_sorted_total_word_count_grouped_by_author = word_count_grouped_by_author.head(15)
fig = top_10_sorted_total_word_count_grouped_by_author.plot.barh()
nameAndSave(top_10_sorted_total_word_count_grouped_by_author.plot.barh(), "Word Count", "Author",
            "Who sent the most words?", 3)

# Average number of words per message for everyone?
plt.figure(figsize=(15, 2)) # To ensure that the bar plot fits in the output cell of a Jupyter notebook
word_count_value_counts = data['Word_Count'].value_counts()
top_40_word_count_value_counts = word_count_value_counts.head(40)
fig = top_40_word_count_value_counts.plot.bar()
nameAndSave(fig, 'Word Count', 'Frequency',
            'Average Number of Words per Text', 4)

# Create a nested dictionary to store every word spoken for every person, and how many times they said the word
unique_authors = data.Author.unique()
authors_words = {}

for author in unique_authors:
    authors_words[author] = {}

for index, row in data.iterrows():

    author = row['Author']
    if isinstance(row['Words'], float):
        continue

    for word in row['Words']:
        # Turn words to lowercase and strip punctuation
        word = word.lower()
        word = word.translate(str.maketrans('', '', string.punctuation))

        # Add to word count for word specified
        if word in authors_words[author] and len(word) > 6 and word != 'omitted':
            authors_words[author][word] += 1
        else:
            authors_words[author][word] = 1

# Create a .csv dataframe for the top 10 most common words for each author
top_10_most_common = {}
for author in authors_words:
    top_10_most_common[author] = dict(Counter(authors_words[author]).most_common(10))
    temp = pd.DataFrame.from_dict(top_10_most_common[author], orient='index', columns=[author])
    temp.to_csv('csv_output/tables/individual_common_words/' + author + '.csv', encoding ='utf=8')

# Create three dataframes - measuring average words per message, letters per message and letters per word
# for each author
authors_words_per_message = {}
for author in unique_authors:
    authors_words_per_message[author] = data.loc[data['Author'] == author, 'Word_Count'].sum() / author_value_counts[author]
words_per_message_df = pd.DataFrame.from_dict(authors_words_per_message, orient='index', columns=['Avg. Words per Message'])
words_per_message_df.to_csv('csv_output/tables/individual_per_message/words_per_message.csv', encoding ='utf=8')

authors_letters_per_message = {}
for author in unique_authors:
    authors_letters_per_message[author] = data.loc[data['Author'] == author, 'Letter_Count'].sum() / author_value_counts[author]
letters_per_message_df = pd.DataFrame.from_dict(authors_letters_per_message, orient='index', columns=['Avg. Letters per Message'])
letters_per_message_df.to_csv('csv_output/tables/individual_per_message/letters_per_message.csv', encoding ='utf=8')

authors_letters_per_word = {}
for author in unique_authors:
    authors_letters_per_word[author] = data.loc[data['Author'] == author, 'Letter_Count'].sum() / data.loc[data['Author'] == author, 'Word_Count'].sum()
letters_per_word_df = pd.DataFrame.from_dict(authors_letters_per_word, orient='index', columns=['Avg. Letters per Word'])
letters_per_word_df.to_csv('csv_output/tables/individual_per_message/letters_per_word.csv', encoding ='utf=8')

# The below code creates a Jupyter notebook that displays the created data,
# then converts it into an .html and stores it in output_final
number_messages = str(len(data.index))
number_authors = str(data['Author'].nunique())
number_words = str(data['Word_Count'].sum())

text_0 = "Your group chat has a total of **" + number_messages + "** messages and **" + number_words + \
         "** words across **" + number_authors + "** unique authors!"

text_1 = """First, let's see who has sent the most individual text messages to the group. Here's a graph:
![image fig1](../images/fig2.png)
"""

text_2 = """Next, let's see who has sent the most individual **media** (audio, video, photo) messages. Who 
sends the most memes?
![image fig1](../images/fig1.png)
"""

text_3 = """Did you see any differences between the last two graphs? Maybe, maybe not. Turns out WhatsApp's classification
of individual text messages might not be the best measure of who talks the most. Instead, word count might be better...
![image fig3](../images/fig3.png)
"""

text_4 = """Do you want to see how long the usual text message in the group is? Do the members prefer long sentences,
or short replies?
![image fig4](../images/fig4.png)
"""

text_5 = """Next, let's see the days in which the group talked the most. Do you recognize any of them?
![image fig5](../images/fig5.png)
"""

text_6 = """Hate not getting a reply? Here's a list of times where you should send a message in order to maximize
your chances of someone being there.
![image fig6](../images/fig6.png)
"""

text_7 = """Curious about the vocabulary of each group member? Here is the top 10 words spoken by each person that is
longer than 5 words. (To filter out words like is, that, then, etc) See any catch phrases?
"""

code_0 = """import pandas as pd
import os
for file in os.listdir("../csv_output/tables/individual_common_words"):
    if file.endswith(".csv"):
        display(pd.read_csv("../csv_output/tables/individual_common_words/" + file))
"""

text_8 = """Who uses the most letters/words per message? Who uses the biggest words? Here are some tables.
"""

code_1 = """for file in os.listdir("../csv_output/tables/individual_per_message"):
    if file.endswith(".csv"):
        display(pd.read_csv("../csv_output/tables/individual_per_message/" + file))
"""

nb = nbf.v4.new_notebook()
nb['cells'] = [nbf.v4.new_markdown_cell(text_0),
               nbf.v4.new_markdown_cell(text_1),
               nbf.v4.new_markdown_cell(text_2),
               nbf.v4.new_markdown_cell(text_3),
               nbf.v4.new_markdown_cell(text_4),
               nbf.v4.new_markdown_cell(text_5),
               nbf.v4.new_markdown_cell(text_6),
               nbf.v4.new_markdown_cell(text_7),
               nbf.v4.new_code_cell(code_0),
               nbf.v4.new_markdown_cell(text_8),
               nbf.v4.new_code_cell(code_1)]
nbf.write(nb, "output_final/analysis.ipynb")



