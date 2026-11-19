import numpy as np
import streamlit as st
from PIL import Image

max_size = 1000
def load_gray_matrix(file):
    img = Image.open(file).convert('RGB')
    img.thumbnail((max_size, max_size))
    rgb = np.array(img, dtype=float)
    r =  rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    gray = 0.299 * r+ 0.587 *g  + 0.114 *b 
    return gray.astype(np.uint8)
    
def translation_matrix(tx, ty):
    translation = np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0, 1]], dtype=float)
    return translation

def scaling_matrix(k):
    scaling = np.array([[k, 0, 0],
                     [0, k, 0],
                     [0, 0, 1]], dtype=float)
    return scaling

def rotation_matrix(angle):
    a = np.radians(angle)
    c, s = np.cos(a), np.sin(a)
    rotation = np.array([[c,  s, 0],
                     [-s, c, 0],
                     [0,  0, 1]])
    return rotation


def around_center(M, h, w):
    cx, cy = w / 2, h / 2
    transformed = translation_matrix(cx, cy) @ M @ translation_matrix(-cx, -cy)
    return transformed

def apply_transform(img, M):
    h, w = img.shape
    out = np.zeros_like(img)
    M_inv = np.linalg.inv(M)
    for y in range(h):
        for x in range(w):
            sx, sy, _ = M_inv @ [x, y, 1]
            sx, sy = round(sx), round(sy)
            if 0 <= sx < w and 0 <= sy < h:
                out[y, x] = img[sy, sx]
    return out


# Streamlit code
st.title("Image Transformations")

file = st.sidebar.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if file is None:
    st.info("pls Upload photo")
    st.stop()

gray = load_gray_matrix(file)
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
col1.image(gray, caption="Original grayscale")
col2.image(apply_transform(gray, M), caption=caption)
