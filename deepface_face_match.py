import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import io
import base64
import tempfile
import os

def image_to_temp_file(uploaded_file):
    """Convert uploaded file to temporary file for DeepFace processing"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            # Read the uploaded file content
            image = Image.open(uploaded_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to temporary file
            image.save(tmp_file.name, format='JPEG')
            return tmp_file.name
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def compare_faces_deepface(image1_path, image2_path, model_name='VGG-Face'):
    """
    Compare two faces using DeepFace library
    Available models: VGG-Face, Facenet, OpenFace, DeepFace, DeepID, ArcFace, Dlib, SFace
    """
    try:
        # Verify faces using DeepFace
        result = DeepFace.verify(
            img1_path=image1_path,
            img2_path=image2_path,
            model_name=model_name,
            distance_metric='cosine'
        )
        
        # Convert distance to confidence percentage
        distance = result['distance']
        # For cosine distance: lower distance = higher similarity
        confidence = max(0, (1 - distance) * 100)
        
        return {
            'success': True,
            'verified': result['verified'],
            'confidence': confidence,
            'distance': distance,
            'model_used': model_name,
            'threshold': result['threshold']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"DeepFace comparison failed: {str(e)}"
        }

def analyze_deepface_result(result):
    """Analyze DeepFace result and provide interpretation"""
    if not result.get('success'):
        return {
            'match_status': 'ERROR',
            'confidence': 0,
            'message': result.get('error', 'Unknown error occurred'),
            'details': result
        }
    
    confidence = result['confidence']
    verified = result['verified']
    
    if verified and confidence > 80:
        match_status = 'STRONG_MATCH'
        message = f"Strong match detected! Confidence: {confidence:.1f}%"
    elif verified and confidence > 60:
        match_status = 'MATCH'
        message = f"Match verified. Confidence: {confidence:.1f}%"
    elif confidence > 40:
        match_status = 'POSSIBLE_MATCH'
        message = f"Possible match detected. Confidence: {confidence:.1f}%"
    else:
        match_status = 'NO_MATCH'
        message = f"No match detected. Confidence: {confidence:.1f}%"
    
    return {
        'match_status': match_status,
        'confidence': confidence,
        'message': message,
        'verified': verified,
        'details': result
    }

def show_deepface_interface():
    """Display DeepFace face matching interface"""
    st.subheader("🧠 AI Face Match (DeepFace)")
    
    # Model selection
    col_model, col_info = st.columns([2, 1])
    
    with col_model:
        selected_model = st.selectbox(
            "Choose AI Model:",
            ['VGG-Face', 'Facenet', 'OpenFace', 'ArcFace', 'Dlib', 'SFace'],
            index=0,
            help="Different models may give varying results"
        )
    
    with col_info:
        st.info(f"Model: {selected_model}")
    
    # Upload option selection
    upload_mode = st.radio(
        "Choose upload method:",
        ["Compare Two Images", "Upload All Photos at Once"],
        horizontal=True
    )
    
    if upload_mode == "Upload All Photos at Once":
        show_deepface_bulk_upload(selected_model)
        return
    
    # Two image comparison
    show_deepface_two_image_comparison(selected_model)

def show_deepface_two_image_comparison(model_name):
    """Show interface for comparing two images using DeepFace"""
    
    # Create two columns for image upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📸 Upload First Image**")
        image1 = st.file_uploader(
            "Choose first face image",
            type=['jpg', 'jpeg', 'png'],
            key="deepface_image_1"
        )
        
        if image1:
            st.image(image1, caption="First Face Image", width=200)
    
    with col2:
        st.markdown("**📸 Upload Second Image**")
        image2 = st.file_uploader(
            "Choose second face image",
            type=['jpg', 'jpeg', 'png'],
            key="deepface_image_2"
        )
        
        if image2:
            st.image(image2, caption="Second Face Image", width=200)
    
    # Compare faces button
    if st.button("🔍 Compare Faces (DeepFace)", type="primary", disabled=(not image1 or not image2)):
        if image1 and image2:
            with st.spinner(f"Processing with {model_name} model..."):
                # Convert images to temporary files
                temp_path1 = image_to_temp_file(image1)
                temp_path2 = image_to_temp_file(image2)
                
                if temp_path1 and temp_path2:
                    try:
                        # Compare faces
                        result = compare_faces_deepface(temp_path1, temp_path2, model_name)
                        analysis = analyze_deepface_result(result)
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("### 📊 Face Comparison Results")
                        
                        # Status indicator
                        if analysis['match_status'] == 'STRONG_MATCH':
                            st.success(f"✅ {analysis['message']}")
                        elif analysis['match_status'] == 'MATCH':
                            st.success(f"✅ {analysis['message']}")
                        elif analysis['match_status'] == 'POSSIBLE_MATCH':
                            st.warning(f"⚠️ {analysis['message']}")
                        elif analysis['match_status'] == 'NO_MATCH':
                            st.error(f"❌ {analysis['message']}")
                        else:
                            st.error(f"⚠️ {analysis['message']}")
                        
                        # Detailed results
                        col_conf, col_status, col_model = st.columns(3)
                        
                        with col_conf:
                            st.metric("Confidence Score", f"{analysis['confidence']:.1f}%")
                        
                        with col_status:
                            st.metric("Verification", "VERIFIED" if analysis.get('verified', False) else "NOT VERIFIED")
                        
                        with col_model:
                            st.metric("AI Model", model_name)
                        
                        # Technical details
                        with st.expander("🔬 Technical Details"):
                            if result.get('success'):
                                st.json({
                                    'model_used': result.get('model_used', model_name),
                                    'distance_score': result.get('distance', 'N/A'),
                                    'threshold_used': result.get('threshold', 'N/A'),
                                    'verification_result': result.get('verified', False),
                                    'confidence_percentage': f"{analysis['confidence']:.2f}%"
                                })
                            else:
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                        
                    finally:
                        # Clean up temporary files
                        try:
                            if temp_path1 and os.path.exists(temp_path1):
                                os.unlink(temp_path1)
                            if temp_path2 and os.path.exists(temp_path2):
                                os.unlink(temp_path2)
                        except:
                            pass
                else:
                    st.error("❌ Failed to process uploaded images")

def show_deepface_bulk_upload(model_name):
    """Interface for bulk photo upload and comparison using DeepFace"""
    st.markdown("### 📤 Bulk Photo Upload & AI Comparison")
    
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
            confidence_threshold = st.slider("Confidence Threshold (%)", 50, 95, 70)
        with col_set2:
            show_details = st.checkbox("Show detailed results", value=True)
        
        # Start comparison
        if st.button("🚀 Start Bulk AI Comparison", type="primary"):
            with st.spinner(f"Processing bulk face comparison with {model_name}..."):
                process_deepface_bulk_comparison(uploaded_files, comparison_mode, confidence_threshold, show_details, model_name)
    
    elif uploaded_files and len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 images for comparison")
    
    else:
        st.info("📝 Upload multiple face images to start AI-powered bulk comparison")

def process_deepface_bulk_comparison(uploaded_files, mode, threshold, show_details, model_name):
    """Process bulk face comparison using DeepFace based on selected mode"""
    
    st.markdown("---")
    st.markdown("### 📊 Bulk AI Comparison Results")
    
    # Convert all images to temporary files
    temp_files = []
    file_names = []
    
    try:
        for uploaded_file in uploaded_files:
            temp_path = image_to_temp_file(uploaded_file)
            if temp_path:
                temp_files.append(temp_path)
                file_names.append(uploaded_file.name)
        
        if len(temp_files) < 2:
            st.error("❌ Failed to process images. Please try different images.")
            return
        
        results = []
        total_comparisons = 0
        
        if mode == "Compare all images with first image (1 vs All)":
            reference_path = temp_files[0]
            reference_name = file_names[0]
            
            st.markdown(f"**Reference Image:** {reference_name}")
            
            progress_bar = st.progress(0)
            
            for i in range(1, len(temp_files)):
                progress_bar.progress(i / (len(temp_files) - 1))
                
                result = compare_faces_deepface(reference_path, temp_files[i], model_name)
                analysis = analyze_deepface_result(result)
                
                results.append({
                    'pair': f"{reference_name} vs {file_names[i]}",
                    'confidence': analysis['confidence'],
                    'match_status': analysis['match_status'],
                    'message': analysis['message'],
                    'verified': analysis.get('verified', False)
                })
                total_comparisons += 1
        
        elif mode == "Compare all images pairwise (All vs All)":
            total_pairs = len(temp_files) * (len(temp_files) - 1) // 2
            progress_bar = st.progress(0)
            current_pair = 0
            
            for i in range(len(temp_files)):
                for j in range(i + 1, len(temp_files)):
                    progress_bar.progress(current_pair / total_pairs)
                    
                    result = compare_faces_deepface(temp_files[i], temp_files[j], model_name)
                    analysis = analyze_deepface_result(result)
                    
                    results.append({
                        'pair': f"{file_names[i]} vs {file_names[j]}",
                        'confidence': analysis['confidence'],
                        'match_status': analysis['match_status'],
                        'message': analysis['message'],
                        'verified': analysis.get('verified', False)
                    })
                    
                    current_pair += 1
                    total_comparisons += 1
        
        elif mode == "Find best matches (Smart Grouping)":
            best_matches = []
            total_pairs = len(temp_files) * (len(temp_files) - 1) // 2
            progress_bar = st.progress(0)
            current_pair = 0
            
            for i in range(len(temp_files)):
                for j in range(i + 1, len(temp_files)):
                    progress_bar.progress(current_pair / total_pairs)
                    
                    result = compare_faces_deepface(temp_files[i], temp_files[j], model_name)
                    analysis = analyze_deepface_result(result)
                    
                    if analysis['confidence'] >= threshold:
                        best_matches.append({
                            'pair': f"{file_names[i]} vs {file_names[j]}",
                            'confidence': analysis['confidence'],
                            'match_status': analysis['match_status'],
                            'message': analysis['message'],
                            'verified': analysis.get('verified', False)
                        })
                    
                    current_pair += 1
                    total_comparisons += 1
            
            results = sorted(best_matches, key=lambda x: x['confidence'], reverse=True)
        
        # Display results
        if results:
            for idx, result in enumerate(results):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                
                with col1:
                    st.write(f"**{result['pair']}**")
                
                with col2:
                    confidence = result['confidence']
                    if confidence >= threshold:
                        st.success(f"✅ {confidence:.1f}%")
                    else:
                        st.error(f"❌ {confidence:.1f}%")
                
                with col3:
                    if result.get('verified', False):
                        st.success("✓ Verified")
                    else:
                        st.error("✗ Not Verified")
                
                with col4:
                    st.write(result['message'])
                
                if show_details and idx < 5:  # Show details for first 5 results
                    with st.expander(f"Details for {result['pair']}"):
                        st.json({
                            'confidence_score': result['confidence'],
                            'match_status': result['match_status'],
                            'verified': result.get('verified', False),
                            'threshold_used': threshold,
                            'ai_model': model_name,
                            'analysis': result['message']
                        })
            
            # Summary statistics
            st.markdown("#### 📈 Summary Statistics")
            matches = len([r for r in results if r['confidence'] >= threshold])
            verified_matches = len([r for r in results if r.get('verified', False)])
            avg_confidence = sum(r['confidence'] for r in results) / len(results) if results else 0
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                st.metric("Total Comparisons", total_comparisons)
            with col_stat2:
                st.metric("Matches Found", matches)
            with col_stat3:
                st.metric("Verified Matches", verified_matches)
            with col_stat4:
                st.metric("Average Confidence", f"{avg_confidence:.1f}%")
        
        else:
            st.warning("⚠️ No matches found above the specified threshold.")
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass