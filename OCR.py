import easyocr


def getTextByOCR(img_src):
    #这里选用的是繁体中文和简体中文
    reader = easyocr.Reader(['ch_tra'])  # 初始化支持中文和英文的 Reader 对象
    result = reader.readtext(img_src)  # 读取一张图片，参数为图片的绝对地址
    print(f"【OCR】{result}")           #元组+数组
    try:
        Confidence = result[0][2]
        Text = result[0][1]

        return  Text, Confidence
    except:
        return '',''


# Text, Confidence = getTextByOCR("D:\Code\PyCharm\BJAR\img\child_screenshot.png")
# print(Text)             #识别的文字
# print(Confidence)       #置信度

#
# Text, Confidence = getTextByOCR("D:\\Code\\PyCharm\\BJAR\\img\\test_error.png")
# print(len(Text))