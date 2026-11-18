import numpy as np
import streamlit as st
from PIL import Image, ImageOps

MAX_SIZE = 300 # longest side of the image in pixels


# ---------- 1. Image -> grayscale 2D matrix ----------
def load_gray_matrix(file):
    img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")  # fix phone rotation
    img.thumbnail((MAX_SIZE, MAX_SIZE))              # resize first, keeps aspect ratio
    rgb = np.array(img, dtype=float)
    r =  rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    gray = 0.299 * r+ 0.587 *g  + 0.114 *b 
    return gray.astype(np.uint8)


# ---------- 2. Transformation matrices (3x3) ----------
def translation_matrix(tx, ty):
    return np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0, 1]], dtype=float)


def scaling_matrix(k):
    return np.array([[k, 0, 0],
                     [0, k, 0],
                     [0, 0, 1]], dtype=float)


def rotation_matrix(angle):
    a = np.radians(angle)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c,  s, 0],
                     [-s, c, 0],
                     [0,  0, 1]])


def around_center(M, h, w):
    """Make M act around the image centre: move centre to origin, apply M, move back."""
    cx, cy = w / 2, h / 2
    return translation_matrix(cx, cy) @ M @ translation_matrix(-cx, -cy)


# ---------- 3. Apply a transformation to the image ----------
def apply_transform(img, M):
    h, w = img.shape
    out = np.zeros_like(img)                 # black canvas
    M_inv = np.linalg.inv(M)
    for y in range(h):
        for x in range(w):
            # For each output pixel, find which input pixel lands here
            sx, sy, _ = M_inv @ [x, y, 1]
            sx, sy = round(sx), round(sy)
            if 0 <= sx < w and 0 <= sy < h:  # only copy if inside the original image
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