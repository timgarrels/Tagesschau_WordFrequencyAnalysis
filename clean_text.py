import html
from os import listdir
import spacy

SUBTITLE_DIR = "ts_subtitles"

all_files = [path for path in listdir(SUBTITLE_DIR) if ".text" in path]
nlp = spacy.load('de_core_news_sm')

for i, subtitle_file in enumerate(all_files):
  if not i%10:
    print(f"{i}/{len(all_files)}")
  with open(SUBTITLE_DIR + "/" + subtitle_file, "r") as f:
    try:
      text = f.readlines()
      text = html.unescape(text[0])
      tokens = nlp(text)
      words = []
      for token in tokens:
        if token.is_punct or token.is_space:
          # Token is punct or space
          pass
        else:
          words.append(token.text)
      clean_text = ' '.join(words)
    except:
      print(subtitle_file)
      # Reset clean text, otherwise old clean text would be written
      clean_text = ''
  with open(SUBTITLE_DIR + "/" + subtitle_file + ".clean_text", "w") as f:
    f.write(clean_text)

