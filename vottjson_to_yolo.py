import json
import glob
import os

JSON_FILE_PATH = "/Users/bekkuhiroo/Desktop/2022_stu/PhotoACobject_on_road_images/vott_export"
SAVE_FILE_PATH = "/Users/bekkuhiroo/Desktop/vottjson_to_yolo"
ANOTNAME_NUM = {"object":"0"}

for json_path in glob.glob(os.path.join(JSON_FILE_PATH, "*.json")):
  with open(json_path) as f:
    jsn = json.load(f)
    Hsize = jsn['asset']['size']['height']
    Wsize = jsn['asset']['size']['width']

    for anot in jsn['regions']:
      height = float(anot['boundingBox']['height'])/Hsize
      width = float(anot['boundingBox']['width'])/Wsize
      left = float(anot['boundingBox']['left'])/Wsize
      top = float(anot['boundingBox']['top'])/Hsize

      center_x = left + width/2
      center_y = top + height/2
      
      tag_name = anot['tags'][0]
      Totxt_str = ANOTNAME_NUM[tag_name] + " " + str(center_x) + " " + str(center_y) + " " + str(height) + " " + str(width)

      print(Totxt_str)

      txt_name = jsn['asset']['name'][:-4] + ".txt"
      image_path = os.path.join(SAVE_FILE_PATH, txt_name)
      
      with open(image_path, mode='a') as f:
        f.write(Totxt_str+ "\n")

print(len(glob.glob(os.path.join(SAVE_FILE_PATH, "*.txt"))))
print(len(glob.glob(os.path.join(JSON_FILE_PATH, "*.jpg"))))
print(len(glob.glob(os.path.join(JSON_FILE_PATH, "*.png"))))
print("全てにアノテーションされていない場合, 値が異なる")