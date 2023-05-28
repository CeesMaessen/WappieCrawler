import pandas as pd
import re
import dateutil.parser as dparser

def clean_df(df, df_name):
    # Remove if date is empty, since it is a string [] counts as 2 characters
    df = df[df['date'].map(len) > 2].reset_index()


    for i, date in enumerate(df['date']):

        if df_name == 'nine_for_news':
            # Turning the date string into a list and keeping the first entry, which is the publish date
            df['date'][i] = list(date.split(', '))
            df['date'][i] = df['date'][i][0]

            # Replacing some strings
            df['date'][i] = df['date'][i].replace("[<span class=\"date meta-item tie-icon\">", "")
            df['date'][i] = df['date'][i].replace("</span>", "")
            # Replacing dates
            df['date'][i] = df['date'][i].replace("januari", "01")
            df['date'][i] = df['date'][i].replace("februari", "02")
            df['date'][i] = df['date'][i].replace("maart", "03")
            df['date'][i] = df['date'][i].replace("april", "04")
            df['date'][i] = df['date'][i].replace("mei", "05")
            df['date'][i] = df['date'][i].replace("juni", "06")
            df['date'][i] = df['date'][i].replace("juli", "07")
            df['date'][i] = df['date'][i].replace("augustus", "08")
            df['date'][i] = df['date'][i].replace("september", "09")
            df['date'][i] = df['date'][i].replace("oktober", "10")
            df['date'][i] = df['date'][i].replace("november", "11")
            df['date'][i] = df['date'][i].replace("december", "12")
            # Removing time
            day, month, year, time = df['date'][i].split(' ')
            df['date'][i] = day + '-' + month + '-' + year

        if df_name == 'indymedia':
            try:
                # Get dd-mm-yyyy
                year = str(dparser.parse(df['date'][i], fuzzy=True).year)
                month = str(dparser.parse(df['date'][i], fuzzy=True).month)
                day = str(dparser.parse(df['date'][i], fuzzy=True).day)
                df['date'][i] = day + '-' + month + '-' + year
            except:
                # Drop if not able to parse. This means that the row isn't a article
                print(f'dropping {i}')
                df.drop(i, inplace=True)

        if df_name == 'niburu':
            # Turning the date string into a list and keeping the first entry, which is the publish date
            df['date'][i] = list(date.split(', '))
            df['date'][i] = df['date'][i][0]
            try:
                # Get dd-mm-yyyy
                year = str(dparser.parse(df['date'][i], fuzzy=True).year)
                month = str(dparser.parse(df['date'][i], fuzzy=True).month)
                day = str(dparser.parse(df['date'][i], fuzzy=True).day)
                df['date'][i] = day + '-' + month + '-' + year
            except:
                # Drop if not able to parse. This means that the row isn't a article
                print(f'dropping {i}')
                df.drop(i, inplace=True)

        if df_name == 'privacynieuws':
            df['date'][i] = list(date.split(', '))
            df['date'][i] = df['date'][i][0]

            # Have to split again on (" )
            df['date'][i] = list(date.split('" '))
            df['date'][i] = df['date'][i][0]

            # Now we can parse dd-mm-yyyy
            try:
                # Get dd-mm-yyyy
                year = str(dparser.parse(df['date'][i], fuzzy=True).year)
                month = str(dparser.parse(df['date'][i], fuzzy=True).month)
                day = str(dparser.parse(df['date'][i], fuzzy=True).day)
                df['date'][i] = day + '-' + month + '-' + year
            except:
                # Drop if not able to parse. This means that the row isn't a article
                print(f'dropping {i}')
                df.drop(i, inplace=True)

        if df_name == 'frontnieuws':
            # Splitting the date string 3 times. First date entry is the post date
            df['date'][i] = list(date.split(', '))
            df['date'][i] = df['date'][i][0]

            df['date'][i] = list(df['date'][i].split('datetime="'))
            df['date'][i] = df['date'][i][1]

            df['date'][i] = list(df['date'][i].split('T'))
            df['date'][i] = df['date'][i][0]

            try:
                # Get dd-mm-yyyy
                year = str(dparser.parse(df['date'][i], fuzzy=True).year)
                month = str(dparser.parse(df['date'][i], fuzzy=True).month)
                day = str(dparser.parse(df['date'][i], fuzzy=True).day)
                df['date'][i] = day + '-' + month + '-' + year
            except:
                # Drop if not able to parse. This means that the row isn't a article
                print(f'dropping {i}')
                df.drop(i, inplace=True)

    return df


df_nine_for_news = pd.read_csv('results_nine_for_news.csv')
df_nine_for_news = clean_df(df_nine_for_news, df_name='nine_for_news')
df_nine_for_news.to_csv('nine_for_news_clean.csv', index=False)

df_indymedia = pd.read_csv('results_Indymedia.csv')
df_indymedia = clean_df(df_indymedia, df_name='indymedia')
df_indymedia.to_csv('indymedia_clean.csv')

df_niburu = pd.read_csv('results_niburu.csv')
df_niburu = clean_df(df_niburu, df_name='niburu')
df_niburu.to_csv('niburu_clean.csv')

df_frontnieuws = pd.read_csv('results_frontnieuws.csv')
df_frontnieuws = clean_df(df_frontnieuws, df_name='frontnieuws')
df_frontnieuws.to_csv('frontnieuws_clean.csv')


