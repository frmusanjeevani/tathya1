"""
3D Animated Intro Page for Tathya Investigation Intelligence
Modern Three.js animation with auto-redirect to login
"""
import streamlit as st
import time

def show():
    """Display the 3D animated intro page"""
    
    # Hide Streamlit elements and set full screen
    st.markdown("""
    <style>
    .stApp > header {visibility: hidden;}
    .stApp > div:first-child {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        margin: 0px;
        padding: 0px;
    }
    .block-container {
        padding: 0px;
        margin: 0px;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 3D Animation HTML with Three.js
    animation_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tathya Investigation Intelligence</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body, html {
                width: 100%;
                height: 100vh;
                overflow: hidden;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: radial-gradient(ellipse at center, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            }
            
            #container {
                width: 100%;
                height: 100vh;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            #logo-text {
                position: absolute;
                z-index: 100;
                color: white;
                text-align: center;
                opacity: 0;
                transform: translateY(20px);
            }
            
            #logo-text h1 {
                font-size: clamp(2rem, 5vw, 4rem);
                font-weight: 600;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 10px;
                letter-spacing: 2px;
            }
            
            #logo-text p {
                font-size: clamp(1rem, 2.5vw, 1.5rem);
                color: #ffffff;
                opacity: 0.8;
                font-weight: 300;
                transition: all 0.5s ease;
            }
            
            #pause-control {
                position: absolute;
                bottom: 20px;
                right: 20px;
                z-index: 200;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 50px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
                cursor: pointer;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            #pause-control:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }
            
            #loading-bar {
                position: absolute;
                bottom: 50px;
                left: 50%;
                transform: translateX(-50%);
                width: 300px;
                height: 2px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 1px;
                overflow: hidden;
            }
            
            #loading-progress {
                width: 0%;
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
                border-radius: 1px;
                transition: width 0.1s ease;
            }
            
            .particle {
                position: absolute;
                background: rgba(255, 255, 255, 0.6);
                border-radius: 50%;
                pointer-events: none;
            }
            
            @media (max-width: 768px) {
                #logo-text h1 {
                    font-size: 2.5rem;
                }
                #logo-text p {
                    font-size: 1.1rem;
                }
                #loading-bar {
                    width: 250px;
                }
            }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="logo-text">
                <h1>🕵️‍♂️ TATHYA</h1>
                <p id="subtitle">Investigation Intelligence</p>
            </div>
            <div id="loading-bar">
                <div id="loading-progress"></div>
            </div>
            <div id="pause-control" onclick="toggleAnimation()">
                <span id="pause-icon">⏸️</span>
                <span id="pause-text">Pause</span>
            </div>
        </div>
        
        <script>
            // Scene setup
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
            
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setClearColor(0x000000, 0);
            document.getElementById('container').appendChild(renderer.domElement);
            
            // Create animated particles/stars background
            const starsGeometry = new THREE.BufferGeometry();
            const starCount = 800;
            const positions = new Float32Array(starCount * 3);
            const colors = new Float32Array(starCount * 3);
            
            for(let i = 0; i < starCount * 3; i += 3) {
                positions[i] = (Math.random() - 0.5) * 2000;
                positions[i + 1] = (Math.random() - 0.5) * 2000;
                positions[i + 2] = (Math.random() - 0.5) * 2000;
                
                const color = new THREE.Color();
                color.setHSL(Math.random() * 0.2 + 0.5, 0.55, Math.random() * 0.25 + 0.55);
                colors[i] = color.r;
                colors[i + 1] = color.g;
                colors[i + 2] = color.b;
            }
            
            starsGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            starsGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            
            const starsMaterial = new THREE.PointsMaterial({
                size: 2,
                vertexColors: true,
                transparent: true,
                opacity: 0.8
            });
            
            const stars = new THREE.Points(starsGeometry, starsMaterial);
            scene.add(stars);
            
            // Create main 3D logo geometry
            const logoGroup = new THREE.Group();
            
            // Central rotating torus
            const torusGeometry = new THREE.TorusGeometry(1, 0.3, 16, 100);
            const torusMaterial = new THREE.MeshBasicMaterial({
                color: 0x667eea,
                transparent: true,
                opacity: 0.8,
                wireframe: true
            });
            const torus = new THREE.Mesh(torusGeometry, torusMaterial);
            logoGroup.add(torus);
            
            // Orbiting spheres
            const sphereGeometry = new THREE.SphereGeometry(0.1, 8, 6);
            const spheres = [];
            
            for(let i = 0; i < 6; i++) {
                const sphereMaterial = new THREE.MeshBasicMaterial({
                    color: new THREE.Color().setHSL(i / 6, 0.7, 0.6),
                    transparent: true,
                    opacity: 0.9
                });
                const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
                
                const angle = (i / 6) * Math.PI * 2;
                sphere.position.x = Math.cos(angle) * 2;
                sphere.position.z = Math.sin(angle) * 2;
                
                spheres.push(sphere);
                logoGroup.add(sphere);
            }
            
            // Add glow effect
            const glowGeometry = new THREE.SphereGeometry(3, 32, 32);
            const glowMaterial = new THREE.MeshBasicMaterial({
                color: 0x667eea,
                transparent: true,
                opacity: 0.1,
                side: THREE.BackSide
            });
            const glow = new THREE.Mesh(glowGeometry, glowMaterial);
            logoGroup.add(glow);
            
            scene.add(logoGroup);
            camera.position.z = 5;
            
            // Animation variables
            let time = 0;
            let animationPhase = 0;
            let isPaused = false;
            let animationStartTime = Date.now();
            
            // Text sequences for subtitle animation
            const textSequences = [
                "Investigation Intelligence",
                "Advanced Verification",
                "Smart Analytics",
                "Case Management",
                "Document Processing",
                "Risk Assessment",
                "Fraud Detection",
                "Intelligence Platform"
            ];
            let currentTextIndex = 0;
            
            // GSAP Timeline
            const tl = gsap.timeline();
            
            // Initial setup - everything hidden
            gsap.set("#logo-text", { opacity: 0, y: 20 });
            gsap.set(logoGroup.scale, { x: 0, y: 0, z: 0 });
            
            // Animation sequence (extended to 8-9 seconds)
            tl.to(logoGroup.scale, { duration: 1.5, x: 1, y: 1, z: 1, ease: "back.out(1.7)" })
              .to("#logo-text", { duration: 1, opacity: 1, y: 0, ease: "power2.out" }, "-=0.8")
              .to("#loading-progress", { duration: 6, width: "100%", ease: "power2.inOut" }, "-=0.5");
            
            // Text cycling animation
            function cycleText() {
                if (isPaused) return;
                
                const subtitle = document.getElementById('subtitle');
                if (!subtitle) return;
                
                gsap.to(subtitle, {
                    duration: 0.3,
                    opacity: 0,
                    y: -10,
                    ease: "power2.in",
                    onComplete: () => {
                        currentTextIndex = (currentTextIndex + 1) % textSequences.length;
                        subtitle.textContent = textSequences[currentTextIndex];
                        gsap.to(subtitle, {
                            duration: 0.3,
                            opacity: 0.8,
                            y: 0,
                            ease: "power2.out"
                        });
                    }
                });
            }
            
            // Start text cycling after initial animation
            setTimeout(() => {
                if (!isPaused) {
                    window.textCycleInterval = setInterval(cycleText, 800); // Change text every 800ms
                }
            }, 2000);
            
            // Global pause/resume functions
            window.toggleAnimation = function() {
                isPaused = !isPaused;
                const pauseIcon = document.getElementById('pause-icon');
                const pauseText = document.getElementById('pause-text');
                
                if (isPaused) {
                    // Pause timeline animation
                    if (tl) tl.pause();
                    
                    // Update button appearance
                    pauseIcon.textContent = '▶️';
                    pauseText.textContent = 'Resume';
                    
                    // Stop text cycling by clearing intervals
                    if (window.textCycleInterval) {
                        clearInterval(window.textCycleInterval);
                        window.textCycleInterval = null;
                    }
                    
                    // Stop the 3D animation loop
                    window.animationPaused = true;
                    
                } else {
                    // Resume timeline animation
                    if (tl) tl.resume();
                    
                    // Update button appearance
                    pauseIcon.textContent = '⏸️';
                    pauseText.textContent = 'Pause';
                    
                    // Restart text cycling
                    if (!window.textCycleInterval) {
                        window.textCycleInterval = setInterval(cycleText, 800);
                    }
                    
                    // Resume the 3D animation loop
                    window.animationPaused = false;
                }
            };
            
            // Extended fade out animation after 8 seconds
            setTimeout(() => {
                if (!isPaused && !window.animationPaused) {
                    gsap.to("body", { 
                        duration: 0.8, 
                        opacity: 0, 
                        ease: "power2.inOut"
                    });
                }
            }, 8000);
            
            // Initialize animation state
            window.animationPaused = false;
            
            // Animation loop
            function animate() {
                requestAnimationFrame(animate);
                
                // Only animate if not paused
                if (!window.animationPaused && !isPaused) {
                    time += 0.01;
                    
                    // Rotate main torus
                    torus.rotation.x += 0.005;
                    torus.rotation.y += 0.01;
                    
                    // Animate orbiting spheres
                    spheres.forEach((sphere, i) => {
                        const angle = time + (i / 6) * Math.PI * 2;
                        sphere.position.x = Math.cos(angle) * 2;
                        sphere.position.z = Math.sin(angle) * 2;
                        sphere.position.y = Math.sin(angle * 2) * 0.5;
                        sphere.rotation.x += 0.02;
                        sphere.rotation.y += 0.01;
                    });
                    
                    // Animate background stars
                    stars.rotation.x += 0.0005;
                    stars.rotation.y += 0.0003;
                    
                    // Pulsing glow effect
                    glow.material.opacity = 0.05 + Math.sin(time * 2) * 0.03;
                    
                    // Camera slight movement
                    camera.position.x = Math.sin(time * 0.5) * 0.1;
                    camera.position.y = Math.cos(time * 0.3) * 0.1;
                }
                
                // Always render the scene
                renderer.render(scene, camera);
            }
            
            // Handle window resize
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
            
            // Start animation
            animate();
            
            // Create floating particles
            function createParticle() {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = '100%';
                particle.style.width = Math.random() * 4 + 2 + 'px';
                particle.style.height = particle.style.width;
                particle.style.animationDuration = Math.random() * 3 + 2 + 's';
                
                document.body.appendChild(particle);
                
                gsap.to(particle, {
                    duration: Math.random() * 3 + 2,
                    y: -window.innerHeight - 100,
                    x: (Math.random() - 0.5) * 200,
                    opacity: 0,
                    ease: "none",
                    onComplete: () => {
                        document.body.removeChild(particle);
                    }
                });
            }
            
            // Generate particles periodically
            setInterval(createParticle, 200);
        </script>
    </body>
    </html>
    """
    
    # Display the animation
    st.components.v1.html(animation_html, height=800, scrolling=False)
    
    # Auto-redirect using Streamlit's sleep and rerun
    if "intro_start_time" not in st.session_state:
        st.session_state.intro_start_time = time.time()
    
    # Check if 9 seconds have passed (extended duration)
    elapsed = time.time() - st.session_state.intro_start_time
    if elapsed >= 9.0:
        st.session_state.show_intro = False
        del st.session_state.intro_start_time  # Clean up
        st.rerun()
    
    # Use auto-refresh to check timing
    time.sleep(0.1)
    st.rerun()