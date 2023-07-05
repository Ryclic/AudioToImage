import requests

image = requests.get("https://www.ldoceonline.com/media/english/illustration/baby.jpg?version=1.2.53", headers={'User-Agent': 'Foo bar'})

print(image.status_code)

# from moviepy.editor import *
# import os
# mylist = [1, 2, 3, 4, 5]

# for i in range(len(mylist)):
#     print(i)
# # clips = []
# img = ImageClip(os.getcwd() + "/photos/communication/communication0.png").set_duration(4)
# # img2 = ImageClip(os.getcwd() + "/photos/consider/consider0.jpeg").set_duration(2)
# img = img.set_start(19, change_end = True)
# # img2 = img2.set_start(6, change_end = True)
# clips.append(img)
# # clips.append(img2)

# # final_clip = concatenate_videoclips(clips)
# img.write_videofile("theTest.mp4", fps =24)