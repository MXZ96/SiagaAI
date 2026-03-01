"""
Modul Analisis Multi-Feature Hybrid untuk Klasifikasi Bencana Alam Tingkat Lanjut.

Modul ini mengekstrak fitur dari gambar menggunakan pendekatan hybrid:
1. Analisis Warna (HSV) - Extended
2. Analisis Tekstur (GLCM)
3. Edge & Struktur Analysis
4. Deteksi Spesifik Objek (Lava, Cone, Smoke, Foam, Horizon, Flatness)

Author: SiagaAI Team
"""

import base64
import io
import numpy as np
from PIL import Image
import cv2
import math


def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode gambar dari format base64 ke array numpy."""
    try:
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Resize for faster processing
        pil_image = pil_image.resize((300, 300))
        
        rgb_image = pil_image.convert('RGB')
        image_array = np.array(rgb_image)
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return bgr_image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def analyze_hsv_colors(image: np.ndarray) -> dict:
    """
    Analisis warna menggunakan HSV color space - Extended version.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h_channel = hsv[:, :, 0]  # Hue: 0-179
    s_channel = hsv[:, :, 1]  # Saturation: 0-255
    v_channel = hsv[:, :, 2]  # Value: 0-255
    
    height, width = h_channel.shape
    total_pixels = height * width
    
    # Normalize
    s_norm = s_channel / 255.0
    v_norm = v_channel / 255.0
    
    # Count colors
    merah = oranye = hijau = biru = coklat = abu = putih = 0
    merah_terang = oranye_intens = 0
    
    for i in range(height):
        for j in range(width):
            h = h_channel[i, j]
            s = s_norm[i, j]
            v = v_norm[i, j]
            
            # Skip very dark pixels
            if v < 0.1:
                continue
            
            # Red (Hue 0-20)
            if h <= 20:
                merah += 1
                if s > 0.5 and v > 0.6:
                    merah_terang += 1
            
            # Orange (Hue 20-40)
            if 20 <= h <= 40:
                oranye += 1
                if s > 0.6 and v > 0.5:
                    oranye_intens += 1
            
            # Green (Hue 35-85)
            if 35 <= h <= 85:
                hijau += 1
            
            # Blue (Hue 85-130)
            if 85 <= h <= 130:
                biru += 1
            
            # Brown (Hue 20-35, medium saturation)
            if 20 <= h <= 35 and 0.2 < s < 0.6:
                coklat += 1
            
            # Gray/Abu (low saturation)
            if s < 0.3 and v > 0.3:
                abu += 1
            
            # White (high value, low saturation)
            if v > 0.8 and s < 0.2:
                putih += 1
    
    effective_pixels = total_pixels * 0.85
    
    return {
        "merah": round((merah / effective_pixels) * 100, 2),
        "merah_terang": round((merah_terang / effective_pixels) * 100, 2),
        "oranye": round((oranye / effective_pixels) * 100, 2),
        "oranye_intens": round((oranye_intens / effective_pixels) * 100, 2),
        "hijau": round((hijau / effective_pixels) * 100, 2),
        "biru": round((biru / effective_pixels) * 100, 2),
        "coklat": round((coklat / effective_pixels) * 100, 2),
        "abu": round((abu / effective_pixels) * 100, 2),
        "putih": round((putih / effective_pixels) * 100, 2),
        "avg_saturation": round(np.mean(s_norm) * 100, 2),
        "avg_value": round(np.mean(v_norm) * 100, 2)
    }


def calculate_glcm_features(gray_image: np.ndarray) -> dict:
    """
    Ekstrak fitur tekstur menggunakan GLCM.
    """
    # Quantize to 8 levels
    levels = 8
    gray_quantized = (gray_image / 256 * levels).astype(np.uint8)
    
    # Compute GLCM for horizontal adjacency
    glcm = np.zeros((levels, levels), dtype=np.float64)
    
    height, width = gray_quantized.shape
    for i in range(height):
        for j in range(width - 1):
            glcm[gray_quantized[i, j], gray_quantized[i, j + 1]] += 1
    
    glcm = glcm / glcm.sum() if glcm.sum() > 0 else glcm
    
    # Calculate features
    # 1. Contrast
    contrast = 0
    for i in range(levels):
        for j in range(levels):
            contrast += (i - j) ** 2 * glcm[i, j]
    
    # 2. Energy
    energy = np.sum(glcm ** 2)
    
    # 3. Homogeneity
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


def analyze_edges_and_structure(image: np.ndarray, gray: np.ndarray) -> dict:
    """
    Edge detection dan analisis struktur.
    """
    # Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    height, width = edges.shape
    total_pixels = height * width
    edge_pixels = np.sum(edges > 0)
    edge_density = (edge_pixels / total_pixels) * 100
    
    # Analyze edge directions
    horizontal_edges = 0
    vertical_edges = 0
    irregular_edges = 0
    
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            if edges[i, j] > 0:
                above = edges[i-1, j] > 0
                below = edges[i+1, j] > 0
                left = edges[i, j-1] > 0
                right = edges[i, j+1] > 0
                
                if above or below:
                    vertical_edges += 1
                if left or right:
                    horizontal_edges += 1
                if (above and not below) or (not above and below):
                    irregular_edges += 1
    
    total_dir_edges = horizontal_edges + vertical_edges
    horizontal_ratio = horizontal_edges / max(total_dir_edges, 1)
    vertical_ratio = vertical_edges / max(total_dir_edges, 1)
    irregular_ratio = irregular_edges / max(edge_pixels, 1)
    
    # Detect building damage (many irregular edges)
    building_damage = irregular_ratio > 0.3 and edge_density > 20
    
    # Detect slope pattern (diagonal edges)
    # Simple slope detection via edge direction variance
    slope_pattern = abs(horizontal_ratio - vertical_ratio) < 0.2 and edge_density > 15
    
    return {
        "edge_density": round(edge_density, 2),
        "horizontal_ratio": round(horizontal_ratio, 4),
        "vertical_ratio": round(vertical_ratio, 4),
        "irregular_ratio": round(irregular_ratio, 4),
        "building_damage": building_damage,
        "slope_pattern": slope_pattern,
        "wave_pattern": horizontal_ratio > 0.55
    }


def detect_lava(features: dict) -> dict:
    """
    Deteksi lava berdasarkan warna merah terang/oranye intens.
    """
    merah_terang = features.get("merah_terang", 0)
    oranye_intens = features.get("oranye_intens", 0)
    avg_sat = features.get("avg_saturation", 0)
    
    # Lava indicators: bright red/orange with high saturation
    lava_score = 0
    if merah_terang > 10:
        lava_score += 0.4
    if oranye_intens > 10:
        lava_score += 0.4
    if avg_sat > 50:
        lava_score += 0.2
    
    return {
        "lava_detected": lava_score >= 0.6,
        "lava_score": round(lava_score, 2)
    }


def detect_cone_shape(image: np.ndarray) -> dict:
    """
    Deteksi bentuk segitiga (cone shape) - kemungkinan gunung.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Find contours
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cone_detected = False
    cone_score = 0
    
    for contour in contours:
        # Get bounding rect
        x, y, w, h = cv2.boundingRect(contour)
        
        # Check if it's roughly triangular (height > width, pointed top)
        if h > 30 and w > 30 and h > w:
            # Check aspect ratio
            aspect_ratio = h / w
            if aspect_ratio > 1.2:
                # Check if apex is at top
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) >= 3 and len(approx) <= 6:
                    cone_detected = True
                    cone_score = min(0.8, (aspect_ratio / 2))
                    break
    
    return {
        "cone_shape_detected": cone_detected,
        "cone_score": round(cone_score, 2)
    }


def detect_smoke_advanced(features: dict, texture: dict, edge: dict) -> dict:
    """
    Deteksi asap lanjutan.
    """
    abu_tinggi = features.get("abu", 0) > 12
    sat_rendah = features.get("avg_saturation", 100) < 40
    edge_rendah = edge.get("edge_density", 100) < 18
    contrast_rendah = texture.get("contrast", 100) < 6
    
    smoke_score = 0
    if abu_tinggi:
        smoke_score += 0.3
    if sat_rendah:
        smoke_score += 0.3
    if edge_rendah:
        smoke_score += 0.25
    if contrast_rendah:
        smoke_score += 0.15
    
    return {
        "smoke_detected": smoke_score >= 0.5,
        "smoke_score": round(smoke_score, 2)
    }


def detect_foam(features: dict, edge: dict) -> dict:
    """
    Deteksi foam (busa) - indikator tsunami.
    """
    putih_tinggi = features.get("putih", 0) > 15
    biru_ada = features.get("biru", 0) > 10
    edge_tidak_rata = edge.get("irregular_ratio", 0) > 0.25
    
    foam_score = 0
    if putih_tinggi:
        foam_score += 0.4
    if biru_ada:
        foam_score += 0.3
    if edge_tidak_rata:
        foam_score += 0.3
    
    return {
        "foam_detected": foam_score >= 0.5,
        "foam_score": round(foam_score, 2)
    }


def detect_horizon(image: np.ndarray) -> dict:
    """
    Deteksi garis horizon - pemisah langit dan laut.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    height, width = gray.shape
    
    # Look for horizontal lines at roughly 1/3 to 1/2 of image height
    horizon_candidates = []
    
    for y in range(int(height * 0.3), int(height * 0.7)):
        row = gray[y, :]
        # Check contrast with row above and below
        if y > 0 and y < height - 1:
            above = gray[y-1, :]
            below = gray[y+1, :]
            
            # Count significant transitions
            transitions = np.sum(np.abs(row.astype(int) - above.astype(int)) > 30) + \
                         np.sum(np.abs(row.astype(int) - below.astype(int)) > 30)
            
            if transitions > width * 0.5:
                horizon_candidates.append(y)
    
    horizon_detected = len(horizon_candidates) > 0
    
    return {
        "horizon_detected": horizon_detected,
        "horizon_line_count": len(horizon_candidates)
    }


def detect_surface_flatness(texture: dict, edge: dict) -> dict:
    """
    Deteksi permukaan air datar (banjir).
    """
    homogeneity_tinggi = texture.get("homogeneity", 0) > 0.6
    edge_rendah = edge.get("edge_density", 100) < 12
    wave_rendah = not edge.get("wave_pattern", False)
    
    flatness_score = 0
    if homogeneity_tinggi:
        flatness_score += 0.4
    if edge_rendah:
        flatness_score += 0.35
    if wave_rendah:
        flatness_score += 0.25
    
    return {
        "surface_flat": flatness_score >= 0.5,
        "flatness_score": round(flatness_score, 2)
    }


def classify_disaster(image_data: str) -> dict:
    """
    Klasifikasi bencana menggunakan multi-feature hybrid extraction.
    """
    # Decode image
    image = decode_base64_image(image_data)
    
    if image is None:
        return {
            "success": False,
            "error": "Gambar tidak dapat dibaca"
        }
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Step 1: HSV Color Analysis
    features = analyze_hsv_colors(image)
    print(f"Color Features: {features}")
    
    # Step 2: GLCM Texture Analysis
    texture = calculate_glcm_features(gray)
    print(f"Texture Features: {texture}")
    
    # Step 3: Edge & Structure Analysis
    edge = analyze_edges_and_structure(image, gray)
    print(f"Edge Features: {edge}")
    
    # Step 4: Specific Object Detection
    lava = detect_lava(features)
    cone = detect_cone_shape(image)
    smoke = detect_smoke_advanced(features, texture, edge)
    foam = detect_foam(features, edge)
    horizon = detect_horizon(image)
    flatness = detect_surface_flatness(texture, edge)
    
    print(f"Lava: {lava}, Cone: {cone}, Smoke: {smoke}")
    print(f"Foam: {foam}, Horizon: {horizon}, Flatness: {flatness}")
    
    # Step 5: Calculate probability scores with ULTRA-STRICT validation
    
    # Calculate base scores with stricter weighting
    merah = features.get("merah", 0)
    oranye = features.get("oranye", 0)
    hijau = features.get("hijau", 0)
    biru = features.get("biru", 0)
    coklat = features.get("coklat", 0)
    abu = features.get("abu", 0)
    putih = features.get("putih", 0)
    entropy = texture.get("entropy", 0)
    contrast = texture.get("contrast", 0)
    homogeneity = texture.get("homogeneity", 0)
    energy = texture.get("energy", 0)
    horizontal_edge = edge.get("horizontal_ratio", 0)
    irregular_edge = edge.get("irregular_ratio", 0)
    edge_density = edge.get("edge_density", 0)
    building_damage = edge.get("building_damage", False)
    slope_pattern = edge.get("slope_pattern", False)
    wave_pattern = edge.get("wave_pattern", False)
    
    # STRICT scoring - require multiple strong indicators
    # KEBAKARAN vs GUNUNG BERAPI differentiation:
    # - Kebakaran: Diffuse fire/smoke, scattered red/orange, NO cone shape
    # - Gunung Berapi: Cone shape (mountain peak), lava, concentrated heat source
    
    fire_colors = merah + oranye
    has_cone = cone["cone_shape_detected"]
    
    # ===== KEBAKARAN: Diffuse fire patterns (no mountain) =====
    score_kebakaran = 0
    
    if fire_colors >= 25 and smoke["smoke_detected"] and not has_cone:
        # Fire + smoke + NO cone = KEBAKARAN
        score_kebakaran = 0.95
    elif fire_colors >= 40 and entropy >= 2.5 and not has_cone:
        score_kebakaran = 0.92
    elif fire_colors >= 35 and not has_cone:
        score_kebakaran = 0.88
    elif fire_colors >= 30 and smoke["smoke_score"] >= 0.4 and not has_cone:
        score_kebakaran = 0.82
    elif fire_colors >= 25 and entropy >= 3.0 and not has_cone:
        score_kebakaran = 0.75
    elif fire_colors >= 30 and not has_cone:
        score_kebakaran = 0.65
    else:
        score_kebakaran = (fire_colors / 100) * 0.5 + smoke["smoke_score"] * 0.3
    
    # If there's a cone shape, it's likely volcano not fire
    if has_cone:
        score_kebakaran *= 0.2
    
    # ===== GUNUNG BERAPI: Volcanic eruption (cone + lava) =====
    score_gunung_berapi = 0
    
    if lava["lava_detected"] and has_cone:
        # LAVA + CONE = DEFINITE volcano
        score_gunung_berapi = 0.98
    elif lava["lava_detected"] and smoke["smoke_detected"]:
        score_gunung_berapi = 0.94
    elif has_cone and smoke["smoke_detected"]:
        score_gunung_berapi = 0.90
    elif lava["lava_score"] >= 0.6 and has_cone:
        score_gunung_berapi = 0.88
    elif has_cone and fire_colors >= 20:
        score_gunung_berapi = 0.85
    elif lava["lava_score"] >= 0.5:
        score_gunung_berapi = 0.75
    elif has_cone:
        score_gunung_berapi = 0.70
    else:
        score_gunung_berapi = lava["lava_score"] * 0.4 + cone["cone_score"] * 0.4 + smoke["smoke_score"] * 0.2
    
    # If NO cone shape and just fire, reduce volcano score
    if not has_cone and fire_colors > 25:
        score_gunung_berapi *= 0.3
    
    # Gempa: needs BUILDING DAMAGE + (HIGH IRREGULAR EDGE OR DUST)
    score_gempa = 0
    if building_damage and irregular_edge > 0.35:
        score_gempa = 0.95
    elif building_damage and abu > 20:
        score_gempa = 0.90
    elif building_damage and edge_density > 25:
        score_gempa = 0.85
    elif irregular_edge > 0.4 and abu > 15:
        score_gempa = 0.80
    elif building_damage:
        score_gempa = 0.70
    else:
        score_gempa = irregular_edge * 1.5 + (abu / 100) * 0.5
    
    # Tsunami: needs WAVE PATTERN + (HORIZON OR FOAM OR BLUE)
    score_tsunami = 0
    if wave_pattern and horizon["horizon_detected"] and biru > 15:
        score_tsunami = 0.95
    elif wave_pattern and foam["foam_detected"]:
        score_tsunami = 0.90
    elif wave_pattern and horizontal_edge > 0.6 and biru > 20:
        score_tsunami = 0.85
    elif horizon["horizon_detected"] and foam["foam_detected"]:
        score_tsunami = 0.80
    elif wave_pattern and horizontal_edge > 0.55:
        score_tsunami = 0.70
    else:
        score_tsunami = horizontal_edge * 0.8 + (biru / 100) * 0.5 + foam["foam_score"] * 0.3
    
    # Banjir: needs FLAT SURFACE + (WATER COLOR OR HIGH HOMOGENEITY)
    score_banjir = 0
    if flatness["surface_flat"] and coklat > 25 and homogeneity > 0.6:
        score_banjir = 0.95
    elif flatness["surface_flat"] and biru > 20 and homogeneity > 0.5:
        score_banjir = 0.90
    elif flatness["surface_flat"] and coklat > 20:
        score_banjir = 0.80
    elif homogeneity > 0.65 and coklat > 15 and not wave_pattern:
        score_banjir = 0.75
    elif flatness["flatness_score"] >= 0.6:
        score_banjir = 0.65
    else:
        score_banjir = flatness["flatness_score"] * 0.5 + homogeneity * 0.5 + (coklat / 100) * 0.3
    
    # Tanah Longsor: needs GREEN + BROWN + (IRREGULAR EDGE OR SLOPE)
    score_tanah_longsor = 0
    green_brown = hijau + coklat
    if green_brown >= 40 and irregular_edge > 0.25 and slope_pattern:
        score_tanah_longsor = 0.95
    elif green_brown >= 35 and irregular_edge > 0.3:
        score_tanah_longsor = 0.90
    elif green_brown >= 40 and contrast > 4:
        score_tanah_longsor = 0.85
    elif hijau > 25 and coklat > 20 and irregular_edge > 0.2:
        score_tanah_longsor = 0.75
    elif green_brown >= 30 and slope_pattern:
        score_tanah_longsor = 0.65
    else:
        score_tanah_longsor = (green_brown / 100) * 0.6 + irregular_edge * 1.2
    
    # Apply minimum indicators validation
    min_indicators = {
        "kebakaran": (merah + oranye >= 20) or (smoke["smoke_detected"] and (merah + oranye >= 10)),
        "gunung_berapi": lava["lava_detected"] or (cone["cone_shape_detected"] and smoke["smoke_detected"]),
        "gempa": building_damage or (irregular_edge > 0.2 and abu > 10),
        "tsunami": (wave_pattern and horizontal_edge > 0.4) or (foam["foam_detected"] and biru > 10),
        "banjir": (flatness["surface_flat"] and homogeneity > 0.4) or (coklat > 20 and homogeneity > 0.5),
        "tanah_longsor": (hijau + coklat >= 30 and irregular_edge > 0.15) or (slope_pattern and coklat > 15)
    }
    
    # Penalize scores without minimum indicators
    if not min_indicators["kebakaran"] and score_kebakaran > 0.5:
        score_kebakaran *= 0.4
    if not min_indicators["gunung_berapi"] and score_gunung_berapi > 0.5:
        score_gunung_berapi *= 0.4
    if not min_indicators["gempa"] and score_gempa > 0.5:
        score_gempa *= 0.4
    if not min_indicators["tsunami"] and score_tsunami > 0.5:
        score_tsunami *= 0.4
    if not min_indicators["banjir"] and score_banjir > 0.5:
        score_banjir *= 0.4
    if not min_indicators["tanah_longsor"] and score_tanah_longsor > 0.5:
        score_tanah_longsor *= 0.4
    
    # Cap scores at 0.95
    score_kebakaran = min(score_kebakaran, 0.95)
    score_gunung_berapi = min(score_gunung_berapi, 0.95)
    score_gempa = min(score_gempa, 0.95)
    score_tsunami = min(score_tsunami, 0.95)
    score_banjir = min(score_banjir, 0.95)
    score_tanah_longsor = min(score_tanah_longsor, 0.95)
    
    scores = {
        "kebakaran": round(score_kebakaran, 4),
        "gunung_berapi": round(score_gunung_berapi, 4),
        "gempa": round(score_gempa, 4),
        "tsunami": round(score_tsunami, 4),
        "banjir": round(score_banjir, 4),
        "tanah_longsor": round(score_tanah_longsor, 4)
    }
    
    # Get top 2 predictions
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_2 = [item[0].replace("_", " ").title() for item in sorted_scores[:2]]
    top_score = sorted_scores[0][1]
    
    # Map disaster names
    disaster_names = {
        "kebakaran": "Kebakaran",
        "gunung_berapi": "Erupsi Gunung Berapi",
        "gempa": "Gempa Bumi",
        "tsunami": "Tsunami",
        "banjir": "Banjir",
        "tanah_longsor": "Tanah Longsor"
    }
    
    # Determine category with ULTRA-STRICT threshold
    # Only classify if confidence is VERY HIGH
    threshold = 0.65  # Much higher threshold
    
    # Check if there's significant gap between top 2 scores
    if len(sorted_scores) >= 2:
        score_gap = sorted_scores[0][1] - sorted_scores[1][1]
        if score_gap < 0.20:
            # Too close - require even higher threshold
            threshold = 0.70
        if score_gap < 0.10:
            threshold = 0.75
    
    # Must have minimum indicator for top category
    top_category = sorted_scores[0][0]
    min_indicator_met = min_indicators.get(top_category, False)
    
    # Also require reasonable scores for other categories not to be too close
    if top_score >= threshold and min_indicator_met:
        kategori = sorted_scores[0][0]
        kategori_bencana = disaster_names.get(kategori, kategori.title())
        # Cap confidence based on how close other scores are
        confidence = round(min(top_score * 100, 95), 1)
    else:
        kategori_bencana = "Tidak Teridentifikasi"
        confidence = round(top_score * 100, 1)
    
    # Generate analysis reason
    reasons = {
        "kebakaran": f"Warna merah ({merah:.1f}%) dan oranye ({oranye:.1f}%) dominan dengan entropy tinggi ({entropy:.2f}) mengindikasikan kebakaran",
        "gunung_berapi": f"Deteksi lava ({lava['lava_score']:.2f}) dan bentuk kerucut ({cone['cone_score']:.2f}) dengan indikator asap ({smoke['smoke_score']:.2f})",
        "gempa": f"Kerusakan struktural ({'terdeteksi' if building_damage else 'tidak terdeteksi'}) dengan pola edge tidak beraturan ({irregular_edge*100:.1f}%)",
        "tsunami": f"Pola gelombang ({'terdeteksi' if edge.get('wave_pattern') else 'tidak terdeteksi'}) dengan foam ({foam['foam_score']:.2f}) dan garis horizon ({'ada' if horizon['horizon_detected'] else 'tidak ada'})",
        "banjir": f"Permukaan datar ({flatness['flatness_score']:.2f}) dengan homogenitas tinggi ({homogeneity:.2f}) dan warna coklat ({coklat:.1f}%)",
        "tanah_longsor": f"Warna hijau ({hijau:.1f}%) dan coklat ({coklat:.1f}%) dengan kontras tinggi ({contrast:.2f}) mengindikasikan longsor"
    }
    
    reason = reasons.get(sorted_scores[0][0], "Analisis tidak dapat menentukan jenis bencana")
    
    return {
        "success": True,
        "kategori_bencana": kategori_bencana,
        "confidence_score": f"{confidence}%",
        "top_2_kemungkinan": top_2,
        "skor_detail": {k: f"{v*100:.1f}%" for k, v in scores.items()},
        "analisis_fitur": {
            "warna_dominan": {
                "merah": f"{merah}%",
                "oranye": f"{oranye}%",
                "hijau": f"{hijau}%",
                "biru": f"{biru}%",
                "coklat": f"{coklat}%",
                "abu": f"{abu}%",
                "putih": f"{features.get('putih', 0)}%"
            },
            "tekstur": {
                "contrast": f"{contrast}",
                "energy": f"{texture['energy']}",
                "homogeneity": f"{homogeneity}",
                "entropy": f"{entropy}"
            },
            "edge_density": f"{edge.get('edge_density', 0)}%",
            "deteksi_lava": "Ya" if lava["lava_detected"] else "Tidak",
            "deteksi_cone_shape": "Ya" if cone["cone_shape_detected"] else "Tidak",
            "deteksi_asap": "Ya" if smoke["smoke_detected"] else "Tidak",
            "deteksi_foam": "Ya" if foam["foam_detected"] else "Tidak",
            "deteksi_horizon": "Ya" if horizon["horizon_detected"] else "Tidak",
            "permukaan_air": "Datar" if flatness["surface_flat"] else "Tidak Datar"
        },
        "reason": reason
    }


# Test function
if __name__ == "__main__":
    print("Multi-Feature Hybrid Disaster Classification Module")
    print("=" * 60)
    print("Features implemented:")
    print("1. HSV Color Analysis (Extended)")
    print("2. GLCM Texture Analysis")
    print("3. Edge & Structure Analysis")
    print("4. Specific Object Detection:")
    print("   - Lava Detection")
    print("   - Cone Shape Detection (Mountain)")
    print("   - Smoke Detection")
    print("   - Foam Detection (Tsunami)")
    print("   - Horizon Detection")
    print("   - Surface Flatness Detection")
