import cv2 as cv
from skimage import exposure

from .bot import TgBot, Cfg


Cfg.configure("https://api.telegram.org/", "7120661602:AAEMsYWDRjvOY-53cR9yvnSxSJOJtMXdios")

bot = TgBot()
imgs = []

@bot.handle
def process(update):
    global imgs

    if "message" not in update:
        return
    
    update = update["message"]
    chat_id = update["chat"]["id"]

    if "document" not in update:
        bot.sendMessage(chat_id, "Please send me photo as document (below 20MB)")
        return
    
    update = update["document"]

    if "file_id" not in update:
        return

    fid = update["file_id"]
    path = bot.getFile(fid)
    imgs.append(path)

    print(imgs)
    
    if len(imgs) < 2:
        return

    img = cv.imread(str(imgs[-1]))
    last_img = cv.imread(str(imgs[-2]))
    
    b, g, r = cv.split(img)
    lb, lg, lr = cv.split(last_img)

    nb = exposure.match_histograms(b, lb)
    ng = exposure.match_histograms(g, lg)
    nr = exposure.match_histograms(r, lr)

    img = cv.merge([nb, ng, nr])
    cv.imwrite("/tmp/equalized.png", img)

    print("uploading..")
    resp = bot.sendFile(chat_id, "/tmp/equalized.png")
    print(resp.json())

    for i, img in enumerate(imgs):
        if i < len(imgs) - 1:
            print("deleting..", img)
            img.unlink()

    imgs = imgs[-1:]