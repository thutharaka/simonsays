import json
import analyzer.options as options

# TODO don't hardcode this dingus
IMG_WIDTH = 1920
IMG_HEIGHT = 1080

# If an "image" has only a single word in this keyword list, we assume it's an
# input box
TEXTBOX_KEYWORDS_LIST = [
    "search",
    "message"
]
# If we detect a text element with a keyword within our "image", if the image
# contains less than x number of text we consider it a textbox instead
TEXTBOX_KEYWORDS_TOLERANCE = 2

def cluster():
    # 0. read in img and ocr jsons
    with open(f"{options.DEFAULT_CACHE_DIR}/ip/scr.json", 'r') as img_file:
        img_json = json.load(img_file)
        # print("Image JSON loaded successfully.")
    with open(f"{options.DEFAULT_CACHE_DIR}/ocr/scr.json", 'r') as ocr_file:
        ocr_json = json.load(ocr_file)
        # print("OCR JSON loaded successfully.")
    
    # 1. figure out how much to look up/down per image
    # - filter out too small or funny shapes
    NOISE_THRESHOLD = 0.005
    SKINNY_RATIO_THRESHOLD = 5
    img_compressed_h = img_json["img_shape"][0] 
    img_compressed_w = img_json["img_shape"][1]
    img_area = img_compressed_h * img_compressed_w
    compression_ratio = IMG_HEIGHT / img_compressed_h
    # print(img_area)
    # print(compression_ratio)
    imgs = []
    for img in img_json["compos"]:
        if (
            # The image has to be large enough for it to be a distraction v.s. just
            # a desktop icon/ webpage decoration
            img["width"] * img["height"] > img_area*NOISE_THRESHOLD and
            # The image can't be super skinny or else it's probably an UI element
            (img["width"] / img["height"] < SKINNY_RATIO_THRESHOLD and
             img["height"] / img["width"] < SKINNY_RATIO_THRESHOLD)
        ):
            img["column_min"] = min(round(img["column_min"] * compression_ratio), IMG_WIDTH)
            img["column_max"] = min(round(img["column_max"] * compression_ratio), IMG_WIDTH)
            img["row_min"] = min(round(img["row_min"] * compression_ratio), IMG_HEIGHT)
            img["row_max"] = min(round(img["row_max"] * compression_ratio), IMG_HEIGHT)
            img["height"] = img["row_max"] - img["row_min"]
            img["width"] = img["column_min"] - img["row_min"]
            imgs.append(img)
    # print(imgs)
    
    # 2. for each image and each boundary, look through all OCR texts and see if it's in the image region
    # - make a vertical square and 2 horizontal squares for query
    # - TODO make a x pos index and y pos index for the OCR & sort in order, this will speed up queries
    BUFFER_HORIZONTAL=25
    BUFFER_VERTICAL=100
    
    ocrs = ocr_json["texts"]
    clusters = []
    for img in imgs:
        # cluster:
        # - id: int
        # - texts associated
        cluster = img 
        cluster["texts"] = []
        # Make 2 bounding boxes, horizontal and vertical
        #
        # Do not consider diagonals, since GUI designers are unlikely to place
        # captions for an image on a diagonal to the image
        #
        # Thus 2 boxes are used
        box_hor = {
            "column_min": max(0, img["column_min"] - BUFFER_HORIZONTAL),
            "column_max": min(IMG_WIDTH, img["column_max"] + BUFFER_HORIZONTAL),
            "row_min": img["row_min"],
            "row_max": img["row_max"],
        }
        box_ver = {
            "row_min": max(0, img["row_min"] - BUFFER_VERTICAL),
            "row_max": min(IMG_HEIGHT, img["row_max"] + BUFFER_VERTICAL),
            "column_min": img["column_min"],
            "column_max": img["column_max"],
        }
        # This tracks all text inside our "image"
        #
        # If the only text inside our "image" is e.g. "search", we know this is a
        # search bar and we can ignore this element
        text_inside_img = []
        for ocr in ocrs:
            for x, y in [
                (ocr["column_min"], ocr["row_min"]),
                (ocr["column_max"], ocr["row_min"]),
                (ocr["column_min"], ocr["row_max"]),
                (ocr["column_max"], ocr["row_max"])
            ]:
                is_within_box = (
                    x >= box_ver["column_min"] and x <= box_ver["column_max"] and
                    y >= box_ver["row_min"] and y <= box_ver["row_max"]
                ) or (
                    x >= box_hor["column_min"] and x <= box_hor["column_max"] and
                    y >= box_hor["row_min"] and y <= box_hor["row_max"]
                )
                if is_within_box:
                    cluster["texts"].append(ocr)
                    is_text_inside_img = (
                        x >= img["column_min"] and x <= img["column_max"] and
                        y >= img["row_min"] and y <= img["row_max"]
                    ) 
                    if is_text_inside_img:
                        text_inside_img.append(ocr["content"])
                    break
        # If there are:
        # - only a few text within an image
        # - ... and one of the text happens to be e.g. "search" or "message"
        # we ignore the element, as it is likely a search/message text input
        is_textbox = False
        if 0 < len(text_inside_img) <= TEXTBOX_KEYWORDS_TOLERANCE:
            for text in text_inside_img:
                for keyw in TEXTBOX_KEYWORDS_LIST:
                    if text.lower().startswith(keyw):
                        is_textbox = True
        if not is_textbox:
            clusters.append(cluster)
    
    # print(clusters)
    return clusters


