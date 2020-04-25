from os import listdir
import json
import sqlite3


SHOWS = []

TS_SHOW_DIR = "ts_shows"
TS_SUBTITLE_DIR = "ts_subtitles"


def load_shows():
  """Loads show metadata"""
  if not SHOWS:
    for show_metadata_file in listdir(TS_SHOW_DIR):
      with open(TS_SHOW_DIR + "/" + show_metadata_file, "r") as f:
        show_dict = json.loads(f.readline())
        SHOWS.append(show_dict)

def date_from_clean_text_file(path):
  """Looks up the corresponding date of the file"""
  org_subtitle_name = path.split(".")[0]
  for show in SHOWS:
    subtitle_url = show["subtitle_url"]
    if org_subtitle_name in subtitle_url:
      return show["air_date"]

  raise AttributeError(f"No show with such subtitle: {subtitle_url}")

def create_clean_text_file_to_date_association():
  load_shows()
  association = []
  clean_text_files = [path for path in listdir(TS_SUBTITLE_DIR) if ".clean_text" in path]
  for clean_text_file in clean_text_files:
    association.append((clean_text_file, date_from_clean_text_file(clean_text_file)))
  return association

def text_to_word_frequencies(text):
  """Returns a dict of word in the text with their count as value"""
  words = text.split(" ")
  uq_words = set(words)
  frequencies = {}.fromkeys(uq_words)
  for key in frequencies.keys():
    count = words.count(key)
    frequencies[key] = count
  return frequencies

def main():
  db_conn = sqlite3.connect("word_frequency.db")
  db_cursor = db_conn.cursor()
  # Create DB
  try:
    db_cursor.execute("CREATE TABLE word_count (date text, word text, count integer)")
    db_conn.commit()
  except sqlite3.OperationalError:
    # Table already exists
    pass
  
  association = create_clean_text_file_to_date_association()
  for i, (clean_text_file, date) in enumerate(association):
    if not i%10:
      print(f"{i}/{len(association)}")
    path = TS_SUBTITLE_DIR + "/" + clean_text_file
    with open(path, "r") as f:
      text = f.readline()
    frequencies = text_to_word_frequencies(text)

    for word, count in frequencies.items():
      # Create a word frequency entry in db with date
      word = word.replace("'", '"')
      db_cursor.execute(f"INSERT INTO word_count VALUES ('{date}','{word}',{count})")
    db_conn.commit()
  db_conn .close()

if __name__ == "__main__":
  main()
