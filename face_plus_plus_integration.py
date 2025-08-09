"""
Face++ API Integration for Configuration Panel
Provides face matching capabilities using Face++ cloud service
"""

import requests
import base64
import streamlit as st
from io import BytesIO
from PIL import Image
import json

# Face++ API Configuration
import os
FACE_PLUS_PLUS_API_KEY = os.environ.get("FACE_PLUS_PLUS_API_KEY")
FACE_PLUS_PLUS_API_SECRET = os.environ.get("FACE_PLUS_PLUS_API_SECRET")
FACE_PLUS_PLUS_ENDPOINT = "https://api-us.faceplusplus.com/facepp/v3/compare"

def image_to_base64(image_file):
    """Convert uploaded image file to base64 string without prefix"""
    try:
        # Read image file
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        img_bytes = buffer.getvalue()
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        
        return base64_string
    except Exception as e:
        st.error(f"Error converting image to base64: {str(e)}")
        return None

def validate_base64(base64_string):
    """Validate base64 string format"""
    try:
        # Check if string is valid base64
        base64.b64decode(base64_string)
        return True
    except Exception:
        return False

def compare_faces(image1_base64, image2_base64):
    """
    Compare two faces using Face++ API
    Returns comparison result with confidence score
    """
    try:
        # Check if API credentials are available
        if not FACE_PLUS_PLUS_API_KEY or not FACE_PLUS_PLUS_API_SECRET:
            return {
                'success': False,
                'error': "Face++ API credentials not found. Please check your environment variables."
            }
        
        # Prepare data for API request
        data = {
            'api_key': FACE_PLUS_PLUS_API_KEY,
            'api_secret': FACE_PLUS_PLUS_API_SECRET,
            'image_base64_1': image1_base64,
            'image_base64_2': image2_base64
        }
        
        # Make POST request to Face++ API
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(FACE_PLUS_PLUS_ENDPOINT, data=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'data': result
            }
        else:
            return {
                'success': False,
                'error': f"API request failed with status code: {response.status_code}",
                'response': response.text
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"Error during face comparison: {str(e)}"
        }

def analyze_face_match_result(result):
    """Analyze Face++ API result and provide interpretation"""
    if not result.get('success'):
        return {
            'match_status': 'ERROR',
            'confidence': 0,
            'message': result.get('error', 'Unknown error occurred'),
            'details': result.get('response', '')
        }
    
    data = result.get('data', {})
    
    # Check for API errors
    if 'error_message' in data:
        return {
            'match_status': 'ERROR',
            'confidence': 0,
            'message': data['error_message'],
            'details': data
        }
    
    # Extract confidence score
    confidence = data.get('confidence', 0)
    
    # Determine match status based on confidence
    if confidence > 80:
        match_status = 'MATCH'
        message = f"Strong match detected! Confidence: {confidence:.2f}%"
    elif confidence > 60:
        match_status = 'POSSIBLE_MATCH'
        message = f"Possible match. Confidence: {confidence:.2f}%"
    else:
        match_status = 'NO_MATCH'
        message = f"No match detected. Confidence: {confidence:.2f}%"
    
    return {
        'match_status': match_status,
        'confidence': confidence,
        'message': message,
        'details': data
    }

def show_face_match_interface():
    """Display Face++ face matching interface"""
    st.subheader("🎭 Face Match Intelligence")
    
    # Check Face++ API status first
    api_status = check_face_plus_plus_status()
    
    if not api_status['available']:
        st.error("⚠️ Face++ API Issue Detected")
        st.markdown(f"**Error:** {api_status['error']}")
        st.markdown("""
        **Possible Solutions:**
        1. Verify Face++ API credentials are valid and active
        2. Check if your Face++ account has sufficient credits
        3. Ensure API key permissions include face comparison
        4. Try refreshing your Face++ API key from the console
        """)
        
        if st.button("🔄 Test API Connection"):
            st.rerun()
        return
    
    # Upload option selection
    upload_mode = st.radio(
        "Choose upload method:",
        ["Compare Two Images", "Upload All Photos at Once"],
        horizontal=True
    )
    
    if upload_mode == "Upload All Photos at Once":
        show_bulk_upload_interface()
        return
    
    # Create two columns for image upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📸 Upload First Image**")
        image1 = st.file_uploader(
            "Choose first face image",
            type=['jpg', 'jpeg', 'png'],
            key="face_image_1"
        )
        
        if image1:
            st.image(image1, caption="First Face Image", width=200)
    
    with col2:
        st.markdown("**📸 Upload Second Image**")
        image2 = st.file_uploader(
            "Choose second face image",
            type=['jpg', 'jpeg', 'png'],
            key="face_image_2"
        )
        
        if image2:
            st.image(image2, caption="Second Face Image", width=200)
    
    # Compare faces button
    if st.button("🔍 Compare Faces", type="primary", disabled=(not image1 or not image2)):
        if image1 and image2:
            with st.spinner("Converting images to base64 format..."):
                # Convert images to base64
                base64_1 = image_to_base64(image1)
                base64_2 = image_to_base64(image2)
                
                if base64_1 and base64_2:
                    # Validate base64 strings
                    if validate_base64(base64_1) and validate_base64(base64_2):
                        st.success("✅ Images converted and validated successfully")
                        
                        with st.spinner("Comparing faces using Face++ API..."):
                            # Compare faces
                            result = compare_faces(base64_1, base64_2)
                            analysis = analyze_face_match_result(result)
                            
                            # Display results
                            st.markdown("---")
                            st.subheader("🔍 Face Comparison Results")
                            
                            # Create result display based on match status
                            match_status = analysis['match_status']
                            confidence = analysis['confidence']
                            message = analysis['message']
                            
                            if match_status == 'MATCH':
                                st.success(f"✅ {message}")
                                st.balloons()
                            elif match_status == 'POSSIBLE_MATCH':
                                st.warning(f"⚠️ {message}")
                            elif match_status == 'NO_MATCH':
                                st.error(f"❌ {message}")
                            else:  # ERROR
                                st.error(f"🚫 {message}")
                            
                            # Display detailed results
                            with st.expander("📊 Detailed Results"):
                                st.json(analysis['details'])
                            
                            # Display interpretation
                            st.markdown("**🧠 Interpretation:**")
                            if match_status == 'MATCH':
                                st.markdown("- **Result**: Same person detected")
                                st.markdown("- **Recommendation**: Proceed with verification")
                                st.markdown("- **Risk Level**: Low")
                            elif match_status == 'POSSIBLE_MATCH':
                                st.markdown("- **Result**: Possible same person")
                                st.markdown("- **Recommendation**: Manual review required")
                                st.markdown("- **Risk Level**: Medium")
                            elif match_status == 'NO_MATCH':
                                st.markdown("- **Result**: Different persons detected")
                                st.markdown("- **Recommendation**: Identity verification failed")
                                st.markdown("- **Risk Level**: High")
                            else:
                                st.markdown("- **Result**: Analysis failed")
                                st.markdown("- **Recommendation**: Retry with different images")
                                st.markdown("- **Risk Level**: Unknown")
                    
                    else:
                        st.error("🚫 Invalid base64 format detected. Please try with different images.")
                else:
                    st.error("🚫 Failed to convert images to base64 format.")
    
    # Help section
    with st.expander("ℹ️ Help & Troubleshooting"):
        st.markdown("""
        **Image Requirements:**
        - Clear, well-lit face photos
        - Passport-style or selfie format
        - Supported formats: JPG, JPEG, PNG
        - Face should be clearly visible and not obscured
        
        **Confidence Score Guide:**
        - **80-100%**: Strong match (likely same person)
        - **60-79%**: Possible match (manual review needed)
        - **0-59%**: No match (different persons)
        
        **Common Issues:**
        - Blurry or low-quality images
        - Poor lighting conditions
        - Face partially obscured
        - Multiple faces in image
        - Very small face size
        
        **API Information:**
        - Service: Face++ Cloud API
        - Endpoint: Face Detection & Comparison
        - Method: Deep learning neural networks
        """)

def show_bulk_upload_interface():
    """Interface for bulk photo upload and comparison"""
    st.markdown("### 📤 Bulk Photo Upload & Comparison")
    
    # Multiple file uploader
    uploaded_files = st.file_uploader(
        "Upload multiple face images for comparison",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Upload 2 or more face images to compare against each other"
    )
    
    if uploaded_files and len(uploaded_files) >= 2:
        st.success(f"✅ {len(uploaded_files)} images uploaded successfully")
        
        # Display uploaded images in a grid
        st.markdown("#### 📷 Uploaded Images")
        cols = st.columns(min(4, len(uploaded_files)))
        
        for idx, uploaded_file in enumerate(uploaded_files):
            col_idx = idx % 4
            with cols[col_idx]:
                st.image(uploaded_file, caption=f"Image {idx+1}", width=150)
        
        # Comparison options
        st.markdown("#### 🔍 Comparison Options")
        comparison_mode = st.selectbox(
            "Select comparison mode:",
            [
                "Compare all images with first image (1 vs All)",
                "Compare all images pairwise (All vs All)",
                "Find best matches (Smart Grouping)"
            ]
        )
        
        # Settings
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            confidence_threshold = st.slider("Confidence Threshold (%)", 50, 95, 80)
        with col_set2:
            show_details = st.checkbox("Show detailed results", value=True)
        
        # Start comparison
        if st.button("🚀 Start Bulk Comparison", type="primary"):
            with st.spinner("Processing bulk face comparison..."):
                process_bulk_comparison(uploaded_files, comparison_mode, confidence_threshold, show_details)
    
    elif uploaded_files and len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 images for comparison")
    
    else:
        st.info("📝 Upload multiple face images to start bulk comparison")

def process_bulk_comparison(uploaded_files, mode, threshold, show_details):
    """Process bulk face comparison based on selected mode"""
    
    st.markdown("---")
    st.markdown("### 📊 Bulk Comparison Results")
    
    # Convert all images to base64
    base64_images = []
    file_names = []
    
    for uploaded_file in uploaded_files:
        base64_img = image_to_base64(uploaded_file)
        if base64_img:
            base64_images.append(base64_img)
            file_names.append(uploaded_file.name)
    
    if len(base64_images) < 2:
        st.error("❌ Failed to process images. Please try different images.")
        return
    
    results = []
    
    if mode == "Compare all images with first image (1 vs All)":
        reference_image = base64_images[0]
        reference_name = file_names[0]
        
        st.markdown(f"**Reference Image:** {reference_name}")
        
        for i in range(1, len(base64_images)):
            result = compare_faces(reference_image, base64_images[i])
            analysis = analyze_face_match_result(result)
            
            results.append({
                'pair': f"{reference_name} vs {file_names[i]}",
                'confidence': analysis['confidence'],
                'match_status': analysis['match_status'],
                'message': analysis['message']
            })
    
    elif mode == "Compare all images pairwise (All vs All)":
        for i in range(len(base64_images)):
            for j in range(i + 1, len(base64_images)):
                result = compare_faces(base64_images[i], base64_images[j])
                analysis = analyze_face_match_result(result)
                
                results.append({
                    'pair': f"{file_names[i]} vs {file_names[j]}",
                    'confidence': analysis['confidence'],
                    'match_status': analysis['match_status'],
                    'message': analysis['message']
                })
    
    elif mode == "Find best matches (Smart Grouping)":
        # Find the best matching pairs
        best_matches = []
        for i in range(len(base64_images)):
            for j in range(i + 1, len(base64_images)):
                result = compare_faces(base64_images[i], base64_images[j])
                analysis = analyze_face_match_result(result)
                
                if analysis['confidence'] >= threshold:
                    best_matches.append({
                        'pair': f"{file_names[i]} vs {file_names[j]}",
                        'confidence': analysis['confidence'],
                        'match_status': analysis['match_status'],
                        'message': analysis['message']
                    })
        
        results = sorted(best_matches, key=lambda x: x['confidence'], reverse=True)
    
    # Display results
    if results:
        for idx, result in enumerate(results):
            col1, col2, col3 = st.columns([3, 1, 2])
            
            with col1:
                st.write(f"**{result['pair']}**")
            
            with col2:
                confidence = result['confidence']
                if confidence >= threshold:
                    st.success(f"✅ {confidence:.1f}%")
                else:
                    st.error(f"❌ {confidence:.1f}%")
            
            with col3:
                st.write(result['message'])
            
            if show_details and idx < 5:  # Show details for first 5 results
                with st.expander(f"Details for {result['pair']}"):
                    st.json({
                        'confidence_score': result['confidence'],
                        'match_status': result['match_status'],
                        'threshold_used': threshold,
                        'analysis': result['message']
                    })
        
        # Summary statistics
        st.markdown("#### 📈 Summary Statistics")
        total_comparisons = len(results)
        matches = len([r for r in results if r['confidence'] >= threshold])
        avg_confidence = sum(r['confidence'] for r in results) / total_comparisons if results else 0
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Total Comparisons", total_comparisons)
        with col_stat2:
            st.metric("Matches Found", matches)
        with col_stat3:
            st.metric("Average Confidence", f"{avg_confidence:.1f}%")
    
    else:
        st.warning("⚠️ No matches found above the specified threshold.")

def check_face_plus_plus_status():
    """Check if Face++ API is available and working"""
    try:
        if not FACE_PLUS_PLUS_API_KEY or not FACE_PLUS_PLUS_API_SECRET:
            return {
                'available': False,
                'error': 'Face++ API credentials not found in environment variables'
            }
        
        # Test API connection with minimal request
        data = {
            'api_key': FACE_PLUS_PLUS_API_KEY,
            'api_secret': FACE_PLUS_PLUS_API_SECRET
        }
        
        response = requests.post(
            'https://api-us.faceplusplus.com/facepp/v3/compare',
            data=data,
            timeout=5
        )
        
        if response.status_code == 401:
            return {
                'available': False,
                'error': 'Face++ API authentication failed - invalid credentials'
            }
        elif response.status_code == 403:
            return {
                'available': False,
                'error': 'Face++ API access forbidden - check account permissions'
            }
        elif response.status_code == 429:
            return {
                'available': False,
                'error': 'Face++ API rate limit exceeded - please wait'
            }
        else:
            return {
                'available': True,
                'error': None
            }
            
    except requests.exceptions.Timeout:
        return {
            'available': False,
            'error': 'Face++ API connection timeout'
        }
    except Exception as e:
        return {
            'available': False,
            'error': f'Face++ API connection error: {str(e)}'
        }

def show_face_match_demo():
    """Show a demo interface for Face++ integration"""
    st.markdown("### 🎭 Face Match Intelligence Demo")
    
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        st.markdown("**Features:**")
        st.markdown("- Real-time face comparison")
        st.markdown("- High accuracy detection")
        st.markdown("- Confidence scoring")
        st.markdown("- Detailed analysis reports")
    
    with demo_col2:
        st.markdown("**Use Cases:**")
        st.markdown("- Identity verification")
        st.markdown("- Document authentication")
        st.markdown("- Access control systems")
        st.markdown("- Fraud prevention")
    
    if st.button("🚀 Try Face Matching", key="demo_face_match"):
        show_face_match_interface()