"""
Modul Analisis Fitur Hybrid untuk Klasifikasi Bencana Alam.

Modul ini mengekstrak fitur dari gambar menggunakan pendekatan hybrid:
1. Analisis Warna (HSV)
2. Analisis Tekstur (GLCM)
3. Edge Detection (Canny)
4. Deteksi Asap
5. Deteksi Gelombang

Author: SiagaAI Team
"""

import base64
import io
import numpy as np
from PIL import Image
import cv2
from collections import Counter
import math


def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode gambar dari format base64 ke array numpy."""
    try:
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Resize for faster processing
        pil_image = pil_image.resize((256, 256))
        
        rgb_image = pil_image.convert('RGB')
        image_array = np.array(rgb_image)
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return bgr_image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def analyze_hsv_colors(image: np.ndarray) -> dict:
    """
    Analisis warna menggunakan HSV color space.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h_channel = hsv[:, :, 0]  # Hue: 0-179
    s_channel = hsv[:, :, 1]  # Saturation: 0-255
    v_channel = hsv[:, :, 2]  # Value: 0-255
    
    height, width = h_channel.shape
    total_pixels = height * width
    
    # Normalize
    s_normalized = s_channel / 255.0
    v_normalized = v_channel / 255.0
    
    # Count colors
    merah_count = oranye_count = hijau_count = coklat_count = abu_count = biru_count = 0
    
    for i in range(height):
        for j in range(width):
            h = h_channel[i, j]
            s = s_normalized[i, j]
            v = v_normalized[i, j]
            
            if v < 0.1:
                continue
            
            if h <= 20:
                merah_count += 1
            if 20 <= h <= 40:
                oranye_count += 1
            if 35 <= h <= 85:
                hijau_count += 1
            if 20 <= h <= 35 and s < 0.6:
                coklat_count += 1
            if s < 0.3:
                abu_count += 1
            if 90 <= h <= 130:
                biru_count += 1
    
    effective_pixels = total_pixels * 0.9
    
    return {
        "merah": round((merah_count / effective_pixels) * 100, 2),
        "oranye": round((oranye_count / effective_pixels) * 100, 2),
        "hijau": round((hijau_count / effective_pixels) * 100, 2),
        "coklat": round((coklat_count / effective_pixels) * 100, 2),
        "abu": round((abu_count / effective_pixels) * 100, 2),
        "biru": round((biru_count / effective_pixels) * 100, 2),
        "avg_saturation": round(np.mean(s_normalized) * 100, 2),
        "fire_dominant": round(((merah_count + oranye_count) / effective_pixels) * 100, 2)
    }


def calculate_glcm_features(gray_image: np.ndarray) -> dict:
    """
    Ekstrak fitur tekstur menggunakan GLCM (Gray Level Co-occurrence Matrix).
    """
    # Quantize to 8 levels for faster computation
    levels = 8
    gray_quantized = (gray_image / 256 * levels).astype(np.uint8)
    
    # Compute GLCM for horizontal adjacency
    glcm = np.zeros((levels, levels), dtype=np.float64)
    
    height, width = gray_quantized.shape
    for i in range(height):
        for j in range(width - 1):
            glcm[gray_quantized[i, j], gray_quantized[i, j + 1]] += 1
    
    # Normalize
    glcm = glcm / glcm.sum() if glcm.sum() > 0 else glcm
    
    # Calculate features
    # 1. Contrast
    contrast = 0
    for i in range(levels):
        for j in range(levels):
            contrast += (i - j) ** 2 * glcm[i, j]
    
    # 2. Energy (Angular Second Moment)
    energy = np.sum(glcm ** 2)
    
    # 3. Homogeneity (Inverse Difference Moment)
    homogeneity = 0
    for i in range(levels):
        for j in range(levels):
            homogeneity += glcm[i, j] / (1 + abs(i - j))
    
    # 4. Entropy
    entropy = 0
    for i in range(levels):
        for j in range(levels):
            if glcm[i, j] > 0:
                entropy -= glcm[i, j] * math.log2(glcm[i, j])
    
    return {
        "contrast": round(contrast, 4),
        "energy": round(energy, 4),
        "homogeneity": round(homogeneity, 4),
        "entropy": round(entropy, 4)
    }


def analyze_edges(image: np.ndarray) -> dict:
    """
    Edge detection menggunakan Canny dan analisis pola edge.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    height, width = edges.shape
    total_pixels = height * width
    
    # Calculate edge density
    edge_pixels = np.sum(edges > 0)
    edge_density = (edge_pixels / total_pixels) * 100
    
    # Analyze horizontal vs vertical edges
    horizontal_edges = 0
    vertical_edges = 0
    irregular_edges = 0
    
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            if edges[i, j] > 0:
                # Check neighboring edge pixels
                above = edges[i-1, j] > 0
                below = edges[i+1, j] > 0
                left = edges[i, j-1] > 0
                right = edges[i, j+1] > 0
                
                if above or below:
                    vertical_edges += 1
                if left or right:
                    horizontal_edges += 1
                if (above and below) or (left and right):
                    irregular_edges += 1
    
    total_direction_edges = horizontal_edges + vertical_edges
    if total_direction_edges > 0:
        horizontal_ratio = horizontal_edges / total_direction_edges
        vertical_ratio = vertical_edges / total_direction_edges
    else:
        horizontal_ratio = 0
        vertical_ratio = 0
    
    # Detect wave pattern (repetitive horizontal lines)
    wave_detected = horizontal_ratio > 0.6 and edge_density > 10
    
    return {
        "edge_density": round(edge_density, 2),
        "horizontal_ratio": round(horizontal_ratio, 4),
        "vertical_ratio": round(vertical_ratio, 4),
        "irregular_ratio": round(irregular_edges / max(edge_pixels, 1), 4),
        "wave_detected": wave_detected
    }


def detect_smoke(features: dict, texture: dict, edge: dict) -> dict:
    """
    Deteksi asap berdasarkan fitur warna, tekstur, dan edge.
    """
    # Indikasi asap
    abu_tinggi = features.get("abu", 0) > 15
    saturation_rendah = features.get("avg_saturation", 100) < 35
    edge_rendah = edge.get("edge_density", 100) < 15
    contrast_rendah = texture.get("contrast", 100) < 5
    
    smoke_score = 0
    if abu_tinggi:
        smoke_score += 0.3
    if saturation_rendah:
        smoke_score += 0.3
    if edge_rendah:
        smoke_score += 0.2
    if contrast_rendah:
        smoke_score += 0.2
    
    smoke_detected = smoke_score >= 0.5
    
    return {
        "smoke_detected": smoke_detected,
        "smoke_score": round(smoke_score, 2),
        "reasons": {
            "abu_tinggi": abu_tinggi,
            "saturation_rendah": saturation_rendah,
            "edge_rendah": edge_rendah,
            "contrast_rendah": contrast_rendah
        }
    }


def detect_wave(edge: dict, features: dict) -> dict:
    """
    Deteksi gelombang (tsunami) berdasarkan pola edge dan warna.
    """
    horizontal_dominant = edge.get("horizontal_ratio", 0) > 0.55
    wave_pattern = edge.get("wave_detected", False)
    biru_tinggi = features.get("biru", 0) > 15
    
    wave_score = 0
    if horizontal_dominant:
        wave_score += 0.4
    if wave_pattern:
        wave_score += 0.3
    if biru_tinggi:
        wave_score += 0.3
    
    wave_detected = wave_score >= 0.5
    
    return {
        "wave_detected": wave_detected,
        "wave_score": round(wave_score, 2),
        "reasons": {
            "horizontal_dominant": horizontal_dominant,
            "wave_pattern": wave_pattern,
            "biru_tinggi": biru_tinggi
        }
    }


def classify_disaster(image_data: str) -> dict:
    """
    Klasifikasikan bencana menggunakan hybrid feature extraction.
    """
    # Decode image
    image = decode_base64_image(image_data)
    
    if image is None:
        return {
            "success": False,
            "error": "Gambar tidak dapat dibaca"
        }
    
    # Step 1: HSV Color Analysis
    color_features = analyze_hsv_colors(image)
    print(f"Color Features: {color_features}")
    
    # Step 2: GLCM Texture Analysis
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    texture_features = calculate_glcm_features(gray)
    print(f"Texture Features: {texture_features}")
    
    # Step 3: Edge Detection
    edge_features = analyze_edges(image)
    print(f"Edge Features: {edge_features}")
    
    # Step 4: Smoke Detection
    smoke_result = detect_smoke(color_features, texture_features, edge_features)
    print(f"Smoke Detection: {smoke_result}")
    
    # Step 5: Wave Detection
    wave_result = detect_wave(edge_features, color_features)
    print(f"Wave Detection: {wave_result}")
    
    # Calculate probability scores
    merah = color_features.get("merah", 0)
    oranye = color_features.get("oranye", 0)
    hijau = color_features.get("hijau", 0)
    coklat = color_features.get("coklat", 0)
    abu = color_features.get("abu", 0)
    biru = color_features.get("biru", 0)
    entropy = texture_features.get("entropy", 0)
    contrast = texture_features.get("contrast", 0)
    homogeneity = texture_features.get("homogeneity", 0)
    horizontal_edge = edge_features.get("horizontal_ratio", 0)
    irregular_edge = edge_features.get("irregular_ratio", 0)
    
    # Calculate scores
    score_kebakaran = (merah * 0.3 + oranye * 0.3 + entropy * 0.1 + contrast * 0.1) / 10
    score_banjir = (coklat * 0.4 + homogeneity * 0.2 + horizontal_edge * 0.4) / 10
    score_gunung_berapi = (abu * 0.3 + merah * 0.3 + entropy * 0.2 + (0.3 if smoke_result["smoke_detected"] else 0)) / 10
    score_tanah_longsor = (hijau * 0.3 + coklat * 0.3 + contrast * 0.1 + irregular_edge * 0.1) / 10
    score_tsunami = (horizontal_edge * 0.5 + biru * 0.3 + (0.2 if wave_result["wave_detected"] else 0)) / 10
    
    scores = {
        "Kebakaran": round(score_kebakaran, 4),
        "Banjir": round(score_banjir, 4),
        "Erupsi Gunung Berapi": round(score_gunung_berapi, 4),
        "Tanah Longsor": round(score_tanah_longsor, 4),
        "Tsunami": round(score_tsunami, 4)
    }
    
    # Get top 2 predictions
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_2 = [item[0] for item in sorted_scores[:2]]
    top_score = sorted_scores[0][1]
    
    # Determine category
    threshold = 0.4
    if top_score >= threshold:
        kategori_bencana = sorted_scores[0][0]
        confidence = round(top_score * 100, 1)
    else:
        kategori_bencana = "Tidak Teridentifikasi"
        confidence = round(top_score * 100, 1)
    
    # Generate analysis reason
    reasons = {
        "Kebakaran": f"Detected dominant red/orange colors ({merah + oranye:.1f}%) with high texture entropy ({entropy:.2f}) indicating fire",
        "Banjir": f"Detected brown color ({coklat:.1f}%) with horizontal edge pattern ({horizontal_edge:.1%}) indicating flood water",
        "Erupsi Gunung Berapi": f"Detected gray ({abu:.1f}%) + red ({merah:.1f}%) with smoke indicators" if smoke_result["smoke_detected"] else f"Detected gray ({abu:.1f}%) + red ({merah:.1f}%) indicating volcanic activity",
        "Tanah Longsor": f"Detected green ({hijau:.1f}%) + brown ({coklat:.1f}%) with irregular edges ({irregular_edge:.1%}) indicating landslide",
        "Tsunami": f"Detected horizontal edge pattern ({horizontal_edge:.1%}) + blue color ({biru:.1f}%) indicating tsunami wave",
        "Tidak Teridentifikasi": "No clear disaster indicators detected in the image"
    }
    
    return {
        "success": True,
        "kategori_bencana": kategori_bencana,
        "confidence_score": f"{confidence}%",
        "top_2_kemungkinan": top_2,
        "all_scores": {k: f"{v*100:.1f}%" for k, v in scores.items()},
        "analisis_fitur": {
            "warna_dominan": {
                "merah": f"{merah}%",
                "oranye": f"{oranye}%",
                "hijau": f"{hijau}%",
                "coklat": f"{coklat}%",
                "abu": f"{abu}%",
                "biru": f"{biru}%"
            },
            "tekstur": {
                "contrast": f"{contrast}",
                "energy": f"{texture_features['energy']}",
                "homogeneity": f"{homogeneity}",
                "entropy": f"{entropy}"
            },
            "edge_density": f"{edge_features['edge_density']}%",
            "horizontal_edge_ratio": f"{horizontal_edge*100}%",
            "indikasi_asap": "Ya" if smoke_result["smoke_detected"] else "Tidak",
            "indikasi_gelombang": "Ya" if wave_result["wave_detected"] else "Tidak"
        },
        "reason": reasons.get(kategori_bencana, "Analisis tidak dapat menentukan jenis bencana")
    }


# Test function
if __name__ == "__main__":
    print("Hybrid Disaster Classification Module")
    print("=" * 60)
    print("Features implemented:")
    print("1. HSV Color Analysis")
    print("2. GLCM Texture Analysis")
    print("3. Canny Edge Detection")
    print("4. Smoke Detection")
    print("5. Wave Detection")
