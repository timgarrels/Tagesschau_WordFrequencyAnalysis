from os import listdir
from bs4 import BeautifulSoup

BROKEN = "untertitel256.xml"

SUBTITLE_DIR = "ts_subtitles"


def all_subtitles():
  all_files = listdir(SUBTITLE_DIR)
  for i, subtitle_file in enumerate(all_files):
    if not i%10:
      print(f"{i}/{len(all_files)}")
    subtitle_file_to_text(SUBTITLE_DIR + "/" + subtitle_file)
  

def subtitle_file_to_text(file_path):
  with open(file_path, "r") as f:
    try:
      soup = BeautifulSoup(f)
      tags = []
      tags.extend(soup.find_all("p"))
      tags.extend(soup.find_all("tt:span"))
    except UnicodeDecodeError:
      tags = []

    file_text = ""
    for tag in tags:
      for child in tag.children:
        if isinstance(child, str):
          if "FABstX" in child:
            file_text = ""
            break
          file_text += child
          file_text += " "  # Insert Space between tag texts
        else:
          file_text += " "
  with open(file_path + ".text", "w") as f:
    f.write(file_text)

def main():
  all_subtitles()

if __name__ == "__main__":
  main()
