import numpy as np
import streamlit as st
from PIL import Image

def grayscale(file, size):
    if file is not None:
        img = Image.open(file).convert("RGB")
    else:
        img = Image.open("default.jpg").convert("RGB")
    img.thumbnail((size, size))
    rgb = np.array(img)

    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]

    gray = 0.299 * r + 0.587 * g + 0.114 * b
    gray_matrix= gray.astype(np.uint8)
    return gray_matrix

def translation_matrix(tx, ty):
    translation = np.array([[1, 0, tx],
                            [0, 1, ty],
                            [0, 0, 1]])
    return translation

def scaling_matrix(k):
    scaling = np.array([[k, 0, 0],
                        [0, k, 0],
                        [0, 0, 1]],)
    return scaling

def rotation_matrix(angle):
    a = np.radians(angle)
    c = np.cos(a)
    s = np.sin(a)
    rotation= np.array([[c, s, 0],
                       [-s, c, 0],
                       [0, 0, 1]])
    return rotation

def around_center(M, h, w):
    x = w/2
    y = h/2
    move_center = translation_matrix(-x, -y)
    move_back = translation_matrix(x, y)

    result = move_back @ M @ move_center
    return result

def apply_transform(img, M):
    h, w = img.shape
    result = np.zeros_like(img)
    M = np.linalg.inv(M)

    for y in range(h):
        for x in range(w):
            sx, sy, _ = M @ [x, y, 1]
            sx = round(sx)
            sy = round(sy)

            if sx in range(w) and sy in range(h):
                result[y, x] = img[sy, sx]

    return result
    
def camera_specs(file):
    img = Image.open(file)
    exif = img.getexif()
    exif_ifd = exif.get_ifd(34665)
    st.subheader("Camera Specifications")
    specs = {
        "Camera model": exif.get(272),
        "ISO speed": exif_ifd.get(34855),
        "Focal length": exif_ifd.get(37386)}

    for name, value in specs.items():
        if value is not None:
            if name == "Focal length":
                value = float(value)
                value = f"{value:g} mm"
            st.write(f"**{name}:** {value}")
        else:
            st.write(f"**{name}:** Not available")


# Streamlit code
st.title("Image Transformations")
file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
size = 500
gray = grayscale(file, size)
h, w = gray.shape

choice = st.sidebar.radio("Choose transformation", ["Rotation", "Scaling", "Translation"])

if choice == "Rotation":
    angle = st.sidebar.number_input("Angle", -360.0, 360.0, 45.0)
    M = around_center(rotation_matrix(angle), h, w)
    caption = f"Rotation by {angle} degrees"
elif choice == "Scaling":
    k = st.sidebar.number_input("Scaling factor", 0.1, 5.0, 0.5, step=0.1)
    M = around_center(scaling_matrix(k), h, w)
    caption = f"Scaling by factor {k}"
else:
    tx = st.sidebar.number_input("Move right (pixels, negative = left)", -w, w, 50)
    ty = st.sidebar.number_input("Move down (pixels, negative = up)", -h, h, 30)
    M = translation_matrix(tx, ty)
    caption = f"Translation by tx={tx}, ty={ty} pixels"

col1, col2 = st.columns(2)
col1.image(gray, caption="Grayscaled")
col2.image(apply_transform(gray, M), caption=caption)

if file is not None:
    camera_specs(file)
else:
    camera_specs("default.jpg")
