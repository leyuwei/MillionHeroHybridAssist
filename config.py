# -*- coding:utf-8 -*-


data_directory = "screenshots"

### 1代表灰度处理， 2代表二值化处理，如果需要使用二值化，需要将2放到前面, 0不使用
image_compress_level = (1, 0, 2)

### 0 表示普通识别，配合compress_level 1使用
### 1 标识精确识别，精确识别建议配合image_compress_level 2使用
api_version = (0, 1)

## 图像比例裁剪区域, (left, top, right, bottom)
## 最终裁剪区域可表示为 (image_width * left, image_height * top, image_width * right, image_height * bottom)
crop_areas = {
    '百万英雄': (55/1080, 300/1920, 1025/1080, 1260/1920),
    '冲顶大会': (40/750, 170/1334, 710/750, 865/1334)
}

### baidu orc
app_id = "13486232"
app_key = "KgdmLQVTVTAsBHd12VRaG8wO"
app_secret = "GAnOzrPSpV2573qx4pfZGFkIIGPRG5iM"

### ocr.space
api_key = "6c851da45688957"

### 默认使用百度，每天封顶500次
### 如果你想要使用ocr.space的话，将ocrspace移动到前面,每个api_key每月支持25000次调用
prefer = ("baidu",  "ocrspace")

### enable chrome
enable_chrome = True
