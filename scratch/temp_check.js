
        const API_URL = ""; // Relativa a nuestro host actual
        let currentImagePath = ""; // Guardar la ruta de la imagen actual para Feedback Loop

        // Elementos DOM
        const statusBadge = document.getElementById("statusBadge");
        const statusText = document.getElementById("statusText");
        const searchInput = document.getElementById("searchInput");
        const searchBtn = document.getElementById("searchBtn");
        const previewContainer = document.getElementById("previewContainer");
        const previewImg = document.getElementById("previewImg");
        const placeholderIcon = document.getElementById("placeholderIcon");
        const placeholderText = document.getElementById("placeholderText");
        const loadingContainer = document.getElementById("loadingContainer");
        const resultCard = document.getElementById("resultCard");
        
        // Vistas de resultado
        const exactResultView = document.getElementById("exactResultView");
        const suggestionsResultView = document.getElementById("suggestionsResultView");
        const suggestionsContainer = document.getElementById("suggestionsContainer");
        const manualCodeInput = document.getElementById("manualCodeInput");
        const manualForceBtn = document.getElementById("manualForceBtn");
        
        // Elementos de Feedback y Corrección en Coincidencia Exacta
        const exactConfirmBtn = document.getElementById("exactConfirmBtn");
        const exactCorrectBtn = document.getElementById("exactCorrectBtn");
        const exactCorrectionBox = document.getElementById("exactCorrectionBox");
        const exactManualInput = document.getElementById("exactManualInput");
        const exactManualSaveBtn = document.getElementById("exactManualSaveBtn");
        
        const resCode = document.getElementById("resCode");
        const resPiece = document.getElementById("resPiece");
        const iconPiece = document.getElementById("iconPiece");
        const resPrice = document.getElementById("resPrice");
        const resDesc = document.getElementById("resDesc");
        const resMaterial = document.getElementById("resMaterial");
        const resMode = document.getElementById("resMode");
        
        const cameraInput = document.getElementById("camera-input");
        const galleryInput = document.getElementById("gallery-input");
        
        const captureBtn = document.getElementById("captureBtn");
        const galleryBtn = document.getElementById("galleryBtn");
        const uploadBtn = document.getElementById("uploadBtn");
        const toast = document.getElementById("toast");

        // Elementos de la cámara WebRTC
        const cameraModal = document.getElementById("cameraModal");
        const cameraVideo = document.getElementById("cameraVideo");
        const cameraCanvas = document.getElementById("cameraCanvas");
        const takePhotoBtn = document.getElementById("takePhotoBtn");
        const closeCameraBtn = document.getElementById("closeCameraBtn");
        let videoStream = null;

        // Elementos del visor de catálogo y sugerencias predictivas
        const searchSuggestions = document.getElementById("searchSuggestions");
        const catalogDivider = document.getElementById("catalogDivider");
        const catalogPageContainer = document.getElementById("catalogPageContainer");
        const catalogPageImg = document.getElementById("catalogPageImg");
        const catalogModal = document.getElementById("catalogModal");
        const catalogModalImg = document.getElementById("catalogModalImg");
        const closeCatalogModalBtn = document.getElementById("closeCatalogModalBtn");

        // Pestañas
        const tabBuscar = document.getElementById("tabBuscar");
        const tabEscanear = document.getElementById("tabEscanear");
        const searchTabContent = document.getElementById("searchTabContent");
        const scanTabContent = document.getElementById("scanTabContent");
        const bottomBar = document.getElementById("bottomBar");

        // SVGs dinámicos para los tipos de pieza
        const PIECE_ICONS = {
            PULSERA: `<circle cx="50" cy="50" r="32" fill="none" stroke="var(--color-gold)" stroke-width="4" stroke-dasharray="8,6" />`,
            ANILLO: `<circle cx="50" cy="62" r="20" fill="none" stroke="var(--color-gold)" stroke-width="4"/><polygon points="50,20 62,38 38,38" fill="var(--color-gold)"/>`,
            COLLAR: `<path d="M50,15 C25,15 20,60 50,85 C80,60 75,15 50,15 Z" fill="none" stroke="var(--color-gold)" stroke-width="4"/>`,
            ARETE: `<circle cx="35" cy="40" r="8" fill="var(--color-gold)"/><circle cx="65" cy="40" r="8" fill="var(--color-gold)"/><path d="M35,48 L35,70 M65,48 L65,70" stroke="var(--color-gold)" stroke-width="4" stroke-linecap="round"/>`,
            DEFAULT: `<polygon points="50,15 80,45 50,85 20,45" fill="none" stroke="var(--color-gold)" stroke-width="4"/>`
        };

        // Extrae el tipo de pieza desde la descripción
        function extractPieza(desc) {
            if (!desc) return "PIEZA";
            const d = desc.toUpperCase();
            if (d.includes("PULSERA")) return "PULSERA";
            if (d.includes("ANILLO")) return "ANILLO";
            if (d.includes("COLLAR") || d.includes("GARGANTILLA")) return "COLLAR";
            if (d.includes("ARETE") || d.includes("BROQUEL") || d.includes("ARRACADA")) return "ARETE";
            if (d.includes("DIJE")) return "DIJE";
            if (d.includes("CADENA")) return "CADENA";
            if (d.includes("TOBILLERA")) return "TOBILLERA";
            
            // Fallback: primera palabra
            const words = desc.trim().split(/\s+/);
            if (words.length > 0) {
                return words[0].toUpperCase().replace(/S$/, "");
            }
            return "JOYERÍA";
        }

        // Selecciona el ícono adecuado para la pieza
        function getPieceIconSvg(pieza) {
            const p = pieza.toUpperCase();
            if (p.includes("PULSERA")) return PIECE_ICONS.PULSERA;
            if (p.includes("ANILLO")) return PIECE_ICONS.ANILLO;
            if (p.includes("COLLAR")) return PIECE_ICONS.COLLAR;
            if (p.includes("ARETE")) return PIECE_ICONS.ARETE;
            return PIECE_ICONS.DEFAULT;
        }

        // Mostrar notificación simple
        function showToast(message, isError = false) {
            toast.textContent = message;
            toast.className = "toast" + (isError ? "" : " success");
            toast.style.display = "block";
            setTimeout(() => {
                toast.style.display = "none";
            }, 4000);
        }

        // Resetear UI
        function resetUI() {
            resultCard.style.display = "none";
            loadingContainer.style.display = "none";
            exactResultView.style.display = "none";
            suggestionsResultView.style.display = "none";
            suggestionsContainer.innerHTML = "";
            if (exactCorrectionBox) exactCorrectionBox.style.display = "none";
            if (exactManualInput) exactManualInput.value = "";
            
            // Ocultar catalog divider y visualizador
            if (catalogDivider) catalogDivider.style.display = "none";
            if (catalogPageContainer) catalogPageContainer.style.display = "none";
            if (catalogPageImg) catalogPageImg.src = "";
            if (searchSuggestions) searchSuggestions.style.display = "none";
        }

        // Consultar estado del servidor
        async function checkServerStatus() {
            try {
                const response = await fetch(`${API_URL}/api/status`);
                if (response.ok) {
                    const data = await response.json();
                    statusBadge.className = "status-badge";
                    if (data.free_queries_remaining !== undefined) {
                        statusText.textContent = `● Online (${data.free_queries_remaining} gratis)`;
                    } else {
                        statusText.textContent = "● Online";
                    }
                } else {
                    throw new Error("Offline");
                }
            } catch (error) {
                statusBadge.className = "status-badge offline";
                statusText.textContent = "● Offline";
            }
        }

        // Mostrar datos en la tarjeta de resultados
        function renderResult(data) {
            loadingContainer.style.display = "none";
            
            // Guardar ruta de la imagen si está disponible en la respuesta
            if (data.image_path) {
                currentImagePath = data.image_path;
            }
            

            
            if (data.type === "suggestions") {
                // Renderizar vista de sugerencias (DUDA)
                exactResultView.style.display = "none";
                suggestionsResultView.style.display = "block";
                suggestionsContainer.innerHTML = "";
                
                if (manualCodeInput) {
                    manualCodeInput.value = "";
                }
                
                const productsList = data.products || [];
                productsList.forEach(product => {
                    const price = parseFloat(product["PRECIO venta publico"]) || 0.0;
                    const priceFormatted = `$${price.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
                    const pieza = extractPieza(product.DESCRIPCION || "");
                    
                    const item = document.createElement("div");
                    item.className = "suggestion-item";
                    item.style.display = "flex";
                    item.style.flexDirection = "row";
                    item.style.justifyContent = "space-between";
                    item.style.alignItems = "center";
                    item.style.gap = "12px";
                    
                    item.innerHTML = `
                        <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                            <div class="suggestion-item-top">
                                <span class="suggestion-code">${product.CODIGO || 'N/A'}</span>
                                <span class="suggestion-price">${priceFormatted}</span>
                            </div>
                            <p class="suggestion-desc">${product.DESCRIPCION || 'Sin descripción'}</p>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="suggestion-material">${(product.MATERIAL || 'ACERO').toUpperCase()}</span>
                                <span class="suggestion-material" style="color:var(--color-gold); font-weight:700;">${pieza}</span>
                            </div>
                        </div>
                        <button class="confirm-suggestion-btn" style="background: rgba(229, 195, 132, 0.1); border: 1px solid var(--color-gold); border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--color-gold); transition: all 0.2s; font-size: 14px; font-weight: bold; flex-shrink: 0;" onmouseover="this.style.background='var(--color-gold)'; this.style.color='#0F0F1A';" onmouseout="this.style.background='rgba(229, 195, 132, 0.1)'; this.style.color='var(--color-gold)';">
                            ✓
                        </button>
                    `;
                    
                    const confirmBtn = item.querySelector(".confirm-suggestion-btn");
                    confirmBtn.addEventListener("click", () => {
                        confirmManualCode(product.CODIGO);
                    });
                    
                    suggestionsContainer.appendChild(item);
                });
                
                resMode.textContent = `Reconocimiento: SUGERENCIAS GEMINI`;
                showToast("Se encontraron sugerencias de coincidencia", false);
            } else {
                // Renderizar vista exacta estándar (EXITOSO)
                suggestionsResultView.style.display = "none";
                exactResultView.style.display = "block";
                
                const code = data.CODIGO || data.codigo || "N/A";
                const desc = data.DESCRIPCION || data.descripcion || "Sin descripción disponible";
                const material = data.MATERIAL || data.material || "N/A";
                const price = parseFloat(data["PRECIO venta publico"] || data.precio) || 0.0;
                
                resCode.textContent = code;
                resDesc.textContent = desc;
                resMaterial.textContent = material.toUpperCase();
                resPrice.textContent = `$${price.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
                
                // Mapear Pieza e ícono dinámicamente
                const pieza = extractPieza(desc);
                resPiece.textContent = pieza;
                iconPiece.innerHTML = getPieceIconSvg(pieza);
                
                resMode.textContent = `ⓘ Reconocimiento: ${data.mode || 'GEMINI_REAL'}`;
                showToast("Identificación completada con éxito", false);
                
                // Mostrar página del catálogo si está disponible
                if (data.catalog_page_url) {
                    if (catalogDivider) catalogDivider.style.display = "block";
                    if (catalogPageContainer) catalogPageContainer.style.display = "flex";
                    if (catalogPageImg) catalogPageImg.src = data.catalog_page_url;
                } else {
                    if (catalogDivider) catalogDivider.style.display = "none";
                    if (catalogPageContainer) catalogPageContainer.style.display = "none";
                    if (catalogPageImg) catalogPageImg.src = "";
                }
            }
            
            resultCard.style.display = "flex";
            // Actualizar el estado y contador de consultas inmediatamente
            checkServerStatus();
        }

        // Enviar código al endpoint de confirmación y entrenamiento
        async function confirmManualCode(code) {
            if (!code) {
                showToast("Por favor, ingresa o selecciona un código", true);
                return;
            }
            
            resetUI();
            loadingContainer.style.display = "flex";
            
            try {
                const response = await fetch(`${API_URL}/buscar_codigo_manual`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        codigo: code,
                        image_path: currentImagePath
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    renderResult(data);
                    showToast("Entrenamiento registrado y pieza confirmada", false);
                } else {
                    const errData = await response.json();
                    throw new Error(errData.error || "Error al forzar código");
                }
            } catch (error) {
                loadingContainer.style.display = "none";
                showToast(error.message, true);
            }
        }

        // Buscar producto por código plano
        async function searchProduct(code) {
            if (!code) {
                showToast("Ingresa un código para buscar", true);
                return;
            }
            
            resetUI();
            loadingContainer.style.display = "flex";
            
            try {
                const response = await fetch(`${API_URL}/api/search?code=${encodeURIComponent(code)}`);
                if (response.ok) {
                    const data = await response.json();
                    renderResult(data);
                } else {
                    const errData = await response.json();
                    throw new Error(errData.error || "Código no encontrado");
                }
            } catch (error) {
                loadingContainer.style.display = "none";
                showToast(error.message, true);
            }
        }

        // Subir y procesar archivo de imagen
        async function processAndUploadImage(file) {
            resetUI();
            
            // Mostrar imagen en el visor
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                previewImg.style.display = "block";
                placeholderIcon.style.display = "none";
                placeholderText.style.display = "none";
                previewContainer.classList.add("has-image");
            }
            reader.readAsDataURL(file);
            
            // Mostrar spinner de carga
            loadingContainer.style.display = "flex";

            const formData = new FormData();
            formData.append("image", file);

            try {
                const response = await fetch(`${API_URL}/api/recognize`, {
                    method: "POST",
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    renderResult(data);
                } else {
                    const errData = await response.json();
                    throw new Error(errData.error || "Error al analizar imagen");
                }
            } catch (error) {
                loadingContainer.style.display = "none";
                showToast(error.message, true);
            }
        }

        // Event Listeners para Pestañas
        tabBuscar.addEventListener("click", () => {
            tabBuscar.classList.add("active");
            tabEscanear.classList.remove("active");
            searchTabContent.style.display = "block";
            scanTabContent.style.display = "none";
            bottomBar.style.display = "none";
            resetUI();
        });

        tabEscanear.addEventListener("click", () => {
            tabEscanear.classList.add("active");
            tabBuscar.classList.remove("active");
            scanTabContent.style.display = "flex";
            searchTabContent.style.display = "none";
            bottomBar.style.display = "flex";
            resetUI();
        });

        // Event Listeners para Búsqueda
        searchBtn.addEventListener("click", () => {
            searchProduct(searchInput.value.trim());
        });

        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                searchProduct(searchInput.value.trim());
            }
        });

        // Lógica de Autocompletado / Búsqueda Predictiva con Debounce
        let searchTimeout = null;
        searchInput.addEventListener("input", () => {
            clearTimeout(searchTimeout);
            const query = searchInput.value.trim();
            if (query.length < 2) {
                searchSuggestions.style.display = "none";
                searchSuggestions.innerHTML = "";
                return;
            }

            searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
                    if (response.ok) {
                        const data = await response.json();
                        renderSearchSuggestions(data.products || []);
                    }
                } catch (error) {
                    console.error("Error al buscar sugerencias:", error);
                }
            }, 250);
        });

        // Renderizar el desplegable de sugerencias predictivas
        function renderSearchSuggestions(products) {
            searchSuggestions.innerHTML = "";
            if (products.length === 0) {
                searchSuggestions.style.display = "none";
                return;
            }

            products.forEach(product => {
                const row = document.createElement("div");
                row.className = "suggestion-row";
                const price = parseFloat(product["PRECIO venta publico"]) || 0.0;
                const priceFormatted = `$${price.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
                
                row.innerHTML = `
                    <div class="suggestion-col-left">
                        <span class="suggestion-row-code">${product.CODIGO}</span>
                        <span class="suggestion-row-desc">${product.DESCRIPCION}</span>
                    </div>
                    <span class="suggestion-row-price">${priceFormatted}</span>
                `;

                row.addEventListener("click", () => {
                    searchInput.value = product.CODIGO;
                    searchSuggestions.style.display = "none";
                    searchProduct(product.CODIGO);
                });

                searchSuggestions.appendChild(row);
            });

            searchSuggestions.style.display = "block";
        }

        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener("click", (e) => {
            if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
                searchSuggestions.style.display = "none";
            }
        });

        // Lógica del Visor de Catálogo con Zoom
        if (catalogPageContainer) {
            catalogPageContainer.addEventListener("click", () => {
                if (catalogPageImg.src) {
                    catalogModalImg.src = catalogPageImg.src;
                    catalogModal.style.display = "flex";
                }
            });
        }
        


        if (closeCatalogModalBtn) {
            closeCatalogModalBtn.addEventListener("click", () => {
                catalogModal.style.display = "none";
                catalogModalImg.style.transform = "scale(1)";
                currentScale = 1;
            });
        }

        // Cerrar modal al hacer clic en el fondo
        if (catalogModal) {
            catalogModal.addEventListener("click", (e) => {
                if (e.target === catalogModal || e.target.parentNode === catalogModal) {
                    catalogModal.style.display = "none";
                    catalogModalImg.style.transform = "scale(1)";
                    currentScale = 1;
                }
            });
        }

        // Lógica de Zoom simple por gestos/doble clic
        let currentScale = 1;
        if (catalogModalImg) {
            catalogModalImg.addEventListener("dblclick", () => {
                if (currentScale === 1) {
                    currentScale = 2.5;
                    catalogModalImg.style.transform = "scale(2.5)";
                } else {
                    currentScale = 1;
                    catalogModalImg.style.transform = "scale(1)";
                }
            });
        }

        // Event Listeners para Rescate Manual
        if (manualForceBtn) {
            manualForceBtn.addEventListener("click", () => {
                confirmManualCode(manualCodeInput.value.trim());
            });
        }

        if (manualCodeInput) {
            manualCodeInput.addEventListener("keypress", (e) => {
                if (e.key === "Enter") {
                    confirmManualCode(manualCodeInput.value.trim());
                }
            });
        }
        
        // Event Listeners para Feedback y Corrección en Coincidencia Exacta
        if (exactConfirmBtn) {
            exactConfirmBtn.addEventListener("click", () => {
                const code = resCode.textContent.trim();
                confirmManualCode(code);
            });
        }

        if (exactCorrectBtn) {
            exactCorrectBtn.addEventListener("click", () => {
                if (exactCorrectionBox.style.display === "none" || exactCorrectionBox.style.display === "") {
                    exactCorrectionBox.style.display = "flex";
                    if (exactManualInput) exactManualInput.focus();
                } else {
                    exactCorrectionBox.style.display = "none";
                }
            });
        }

        if (exactManualSaveBtn) {
            exactManualSaveBtn.addEventListener("click", () => {
                confirmManualCode(exactManualInput.value.trim());
            });
        }

        if (exactManualInput) {
            exactManualInput.addEventListener("keypress", (e) => {
                if (e.key === "Enter") {
                    confirmManualCode(exactManualInput.value.trim());
                }
            });
        }

        // Iniciar cámara WebRTC con fallback
        async function startCamera() {
            resetUI();
            
            try {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error("API WebRTC no soportada en este navegador.");
                }
                
                videoStream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: "environment",
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                });
                
                cameraVideo.srcObject = videoStream;
                cameraModal.style.display = "flex";
                showToast("Cámara en vivo activada", false);
            } catch (error) {
                console.warn("[WEBRTC FALLBACK] No se pudo abrir la cámara WebRTC: ", error);
                showToast("Activando selector de cámara nativo...", false);
                cameraInput.click();
            }
        }

        // Detener transmisión de cámara
        function stopCamera() {
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
                videoStream = null;
            }
            cameraVideo.srcObject = null;
            cameraModal.style.display = "none";
        }

        // Tomar foto y capturar bytes
        function capturePhoto() {
            if (!videoStream) return;
            
            const width = cameraVideo.videoWidth || 640;
            const height = cameraVideo.videoHeight || 480;
            cameraCanvas.width = width;
            cameraCanvas.height = height;
            
            const ctx = cameraCanvas.getContext("2d");
            ctx.drawImage(cameraVideo, 0, 0, width, height);
            

            
            cameraCanvas.toBlob((blob) => {
                if (blob) {
                    const file = new File([blob], `capture_${Date.now()}.jpg`, { type: "image/jpeg" });
                    processAndUploadImage(file);
                } else {
                    showToast("Error al capturar la imagen del visor", true);
                }
                stopCamera();
            }, "image/jpeg", 0.92);
        }

        // Event Listeners para Barra de Captura
        captureBtn.addEventListener("click", () => {
            startCamera();
        });

        closeCameraBtn.addEventListener("click", () => {
            stopCamera();
        });

        takePhotoBtn.addEventListener("click", () => {
            capturePhoto();
        });

        galleryBtn.addEventListener("click", () => {
            galleryInput.click();
        });

        uploadBtn.addEventListener("click", () => {
            galleryInput.click();
        });

        cameraInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                processAndUploadImage(file);
            }
        });

        galleryInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                processAndUploadImage(file);
            }
        });

        // Polling de estado del servidor
        checkServerStatus();
        setInterval(checkServerStatus, 5000);

        // Registrar Service Worker para soporte PWA
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(reg => console.log('[PWA] Service Worker registrado en scope:', reg.scope))
                    .catch(err => console.error('[PWA] Error al registrar Service Worker:', err));
            });
        }
    