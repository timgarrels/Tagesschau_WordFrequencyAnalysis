"""Main Tool: Query words to plot frequency over time"""
import sqlite3
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def latest_date(connection):
  c = connection.cursor()
  c.execute("SELECT date from word_count ORDER BY date(date) DESC LIMIT 1")
  return c.fetchone()[0]

def oldest_date(connection):
  c = connection.cursor()
  c.execute("SELECT date from word_count ORDER BY date(date) ASC LIMIT 1")
  return c.fetchone()[0]

def get_word_frequencies(connection, word):
  c = connection.cursor()
  c.execute(f"SELECT date, count from word_count WHERE word = '{word}'")
  return c.fetchall()

def db_date_to_py_date(db_date):
  return datetime.strptime(db_date, "%Y-%m-%d %H:%M:%S").date()

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def data_for_words(words):
  """Retrieves frequency data for words, maps them to date
  Returns a dict with dates as key, value being a dict with words as key and count as value"""
  db_conn = sqlite3.connect("word_frequency.db")
  # Create data for all dates available
  lastest = db_date_to_py_date(latest_date(db_conn))
  oldest = db_date_to_py_date(oldest_date(db_conn))
  data = {}.fromkeys(list(daterange(oldest, lastest)))
  # Do not use default as the dicts would be all the same (by reference)
  for key in data.keys():
    data[key] = {}.fromkeys(words, 0)
  
  for word in words:
    # Get all word frequency data
    result = get_word_frequencies(db_conn, word)
    # Splice it by date
    for date_str, count in result:
      date = db_date_to_py_date(date_str)
      # Add to data
      data[date][word] = count
      # if data[date]:
      #   data[date][word] = count
      # else:
      #   data[date] = {word: count}
  
  db_conn.close()
  return data

def data_per_week(data):
  """Transforms data weekwise"""
  new_data = {}
  for date, word_dict in data.items():
    week_num = date.isocalendar()[1]
    identifier = str(date.year) + "-" + str(week_num)
    key = datetime.strptime(identifier + '-1', "%Y-%W-%w")

    if new_data.get(key, None):
      for word, count in word_dict.items():
        new_data[key][word] += count
    else:
      new_data[key] = word_dict

  return new_data 

def shrink_data_by_factor(data, factor):
  """Reduces the x values by a factor"""
  # Find biggest divisor < factor
  for divisor in reversed(list(range(1, len(data.keys()) + 1))):
    if(len(data.keys()) % divisor == 0):
      if divisor <= factor:
        break
  divisor = factor

  new_data = {}
  # Breaking keys into evenly sized chucks (divisor equals chunk size)
  sorted_keys = sorted(data.keys())
  for i in range(0, len(sorted_keys), divisor):
    chunk = sorted_keys[i:i + divisor]
    for key in chunk:
      word_dict = data[key]
      if new_data.get(chunk[0], None):
        for word, count in word_dict.items():
          new_data[chunk[0]][word] += count
      else:
        new_data[chunk[0]] = word_dict
  return new_data  

def create_plot(words):
  # Get and shrink data
  data = data_for_words(words)
  data = shrink_data_by_factor(data, 25)
  # Labels
  plt.xlabel("Date")
  plt.ylabel("Word-Count")
  
  # Create graphs
  for word in words:
    # Sort by date as dicts are not sorted
    x = sorted(data.keys())
    y = [data[date][word] for date in x]

    # Draw plot and space beneath
    plt.plot_date(x, y, linestyle='solid', marker=None, alpha=(1/len(words))*4)
    plt.fill_between(x, y, alpha=0.2)

  # Design
  plt.gca().spines['top'].set_visible(False)
  plt.gca().spines['right'].set_visible(False)
  plt.legend(words)

  return plt


def main():
  # Words to plot over time
  words = sys.argv[1:]
  if not len(words):
    sys.exit("provide words to plot!")
  plt = create_plot(words)
  plt.show()  

if __name__ == "__main__":
  main()
