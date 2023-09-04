import json
import glob
import os
import shutil
import random
import sys
import urllib.parse

# コマンドライン引数をオプションの形（-X 値／-X）で指定する例
# 以下の辞書で値がTrueのオプションは、続けてその値を指定するもの
# 値がFalseのオプションは何らかのスイッチ（True／False値を持つ）
# 例：python3 kw_args.py -x hoge -y huga -z
options = {'-vs': True, '-vt': True, '-o': True, '-train': True, '-tags': True}
args = {'vs': None, 'vt': None, 'o': None, 'train': 0.8, 'tags': None}  # デフォルト値

for key in options.keys():
    if key in sys.argv:
        index = sys.argv.index(key)
        if options[key]:
            value = sys.argv[index+1]
            if value.startswith('-'):
              print("Option "+key+" must have a value.")
              sys.exit()
            args[key[1:]] = value
            del sys.argv[index:index+2]
        else:
            args[key[1:]] = True
            del sys.argv[index]

VOTT_SOURCE_PATH = args['vs']
VOTT_TARGET_PATH = args['vt']
YOLO_EXPORT_PATH = args['o']
TRAIN_RATIO      = float(args['train'])

if None in args.values():
  print("Usage: python vottjson_to_yolo.py -vs VOTT_SOURCE -vt VOTT_TARGET -o YOLO_EXPORT -train TRAIN_RATIO -tags COMMA_SEPARATED_TAGS")
  print("  -vs VOTT_SOURCE: VoTTのソース接続フォルダ。画像ファイルが含まれている。")
  print("  -vs VOTT_TARGET: VoTTのターゲット接続フォルダ。JSONファイルが含まれている。")
  print("  -o  YOLO_TARGET: YOLOで読み込むアノテーションデータ出力フォルダ。")
  print("  -train TRAIN_RATIO: 学習用に用いる画像の割合。少数で指定する。")
  print("  -tags COMMA_SEPARATED_TAGS: VoTTのアノテーション結果に含まれるタグのリスト。例：foo,baa,hoge")
  sys.exit()

TAGS = args['tags'].split(',')

# YOLO用アノテーションデータと画像の保存ディレクトリ作成
os.makedirs(os.path.join(YOLO_EXPORT_PATH, "train/labels"), exist_ok=True)
os.makedirs(os.path.join(YOLO_EXPORT_PATH, "train/images"), exist_ok=True)
os.makedirs(os.path.join(YOLO_EXPORT_PATH, "valid/labels"), exist_ok=True)
os.makedirs(os.path.join(YOLO_EXPORT_PATH, "valid/images"), exist_ok=True)

# YOLO用アノテーションデータへの変換と保存
for json_file in glob.glob(os.path.join(VOTT_TARGET_PATH, "*.json")):
  with open(json_file) as f:
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
      Totxt_str = str(TAGS.index(tag_name)) + " " + str(center_x) + " " + str(center_y) + " " + str(width) + " " + str(height)

      print(Totxt_str)

      txt_name = jsn['asset']['name'][:-4] + ".txt"
      #txt_name = index + ".txt"
      #index += 1
      img_name = urllib.parse.unquote(jsn['asset']['name'])
      vott_img_file = os.path.join(VOTT_SOURCE_PATH, img_name)
      usage = "train" if random.random() < TRAIN_RATIO else "valid"
      yolo_txt_file = os.path.join(YOLO_EXPORT_PATH, usage, "labels", img_name[:-4] + ".txt")
      yolo_img_file = os.path.join(YOLO_EXPORT_PATH, usage, "images", img_name)

      # copy the img file to YOLO_EXPORT_PATH
      shutil.copy(vott_img_file, yolo_img_file)
      # write annotation data to the txt file corresponding to the img
      with open(yolo_txt_file, mode='w') as f:
        f.write(Totxt_str+ "\n")

print("合計枚数：", len(glob.glob(YOLO_EXPORT_PATH+"/**/*.txt", recursive=True)))
print("train枚数：", len(glob.glob(YOLO_EXPORT_PATH+"/train/labels/*.txt")))
print("valid枚数：", len(glob.glob(YOLO_EXPORT_PATH+"/valid/labels/*.txt")))

