#Generate 50 more realistic-looking sample JPEG images across categories and zip them
from PIL import Image, ImageDraw
import random, os, zipfile

base_dir = "/home/manibalan/Videos/image-library-app/sampleimages/"
os.makedirs(base_dir, exist_ok=True)

categories = ["nature","architecture","people","technology","abstract"]
paths = []

def gradient_image(w, h, c1, c2):
    img = Image.new("RGB",(w,h),c1)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(c1[0] + (c2[0]-c1[0]) * y / h)
        g = int(c1[1] + (c2[1]-c1[1]) * y / h)
        b = int(c1[2] + (c2[2]-c1[2]) * y / h)
        draw.line([(0,y),(w,y)], fill=(r,g,b))
    return img

for i in range(1,51):
    w,h = random.choice([(1200,800),(1000,700),(1280,720)])
    c1 = tuple(random.randint(0,255) for _ in range(3))
    c2 = tuple(random.randint(0,255) for _ in range(3))
    img = gradient_image(w,h,c1,c2)
    
    draw = ImageDraw.Draw(img)
    cat = random.choice(categories)
    text = f"{cat.title()} {i}"
    draw.rectangle([20,h-80,400,h-20], fill=(0,0,0))
    draw.text((30,h-60), text, fill=(255,255,255))
    
    path = os.path.join(base_dir,f"{cat}_{i}.jpg")
    img.save(path,"JPEG",quality=90)
    paths.append(path)

zip_path = "/home/manibalan/Videos/image-library-app/sampleimages/sample_real_images_50.zip"
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:
        z.write(p, os.path.basename(p))

zip_path
