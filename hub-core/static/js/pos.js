let cart = [];
let currentCaja = null;
let selectedPaymentMethod = 'efectivo';
const audioBeep = document.getElementById('beepSound');

// Elements
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const clientInput = document.getElementById('clientInput');
const clientResults = document.getElementById('clientResults');
const clientIdHidden = document.getElementById('clientId');
const cartBody = document.getElementById('cartBody');

// Totals
const subtotalDisplay = document.getElementById('subtotalDisplay');
const discountDisplay = document.getElementById('discountDisplay');
const totalDisplay = document.getElementById('totalDisplay');

// Init
document.addEventListener('DOMContentLoaded', () => {
    checkCajaAbierta();
    setupKeyboardShortcuts();
    setupPaymentMethods();
    setupModals();
    searchInput.focus();

    // Check for clientId in URL
    const urlParams = new URLSearchParams(window.location.search);
    const qClientId = urlParams.get('clientId');
    if (qClientId) {
        selectClientById(qClientId);
    }

    // Fake beep if actual audio file doesn't load/play
    audioBeep.onerror = () => {
        window.fakeBeep = true;
    };
});

async function selectClientById(id) {
    try {
        const res = await fetch(`/api/clientes/${id}`);
        const client = await res.json();
        if (client && !client.error) {
            clientInput.value = client.nombre;
            clientIdHidden.value = client.id;
        }
    } catch (e) { console.error(e); }
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // F2: foco en buscador productos
        if (e.key === 'F2') {
            e.preventDefault();
            searchInput.focus();
        }
        // F3: foco en buscador cliente
        if (e.key === 'F3') {
            e.preventDefault();
            clientInput.focus();
        }
        // F4-F7: Métodos de pago
        if (e.key === 'F4') setPayment('efectivo');
        if (e.key === 'F5') setPayment('tarjeta');
        if (e.key === 'F6') setPayment('transferencia');
        if (e.key === 'F7') setPayment('qr');

        // Enter: Si el modal no está abierto, cobrar. Si está abierto, confirmar.
        if (e.key === 'Enter') {
            const modal = document.getElementById('modalCobro');
            if (!modal.classList.contains('hidden')) {
                document.getElementById('btnConfirmarCobro').click();
            } else if (document.activeElement === searchInput) {
                // If focus is on search and there's 1 active item, select it
                const active = searchResults.querySelector('.active');
                if (active) active.click();
            } else {
                document.getElementById('btnCobrar').click();
            }
        }
        // Esc: Cancelar o cerrar modal
        if (e.key === 'Escape') {
            const modal = document.getElementById('modalCobro');
            if (!modal.classList.contains('hidden')) {
                document.getElementById('btnCerrarModal').click();
            } else {
                document.getElementById('btnCancelar').click();
            }
        }
    });

    // Arrow navigation on search results
    searchInput.addEventListener('keydown', (e) => {
        const items = searchResults.querySelectorAll('.search-item');
        if (!items.length) return;

        let activeIdx = Array.from(items).findIndex(i => i.classList.contains('active'));

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (activeIdx < items.length - 1) activeIdx++;
            updateActiveSearchItem(items, activeIdx);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (activeIdx > 0) activeIdx--;
            updateActiveSearchItem(items, activeIdx);
        }
    });
}

function updateActiveSearchItem(items, idx) {
    items.forEach(i => i.classList.remove('active'));
    if (idx >= 0) items[idx].classList.add('active');
}

function setPayment(method) {
    selectedPaymentMethod = method;
    document.querySelectorAll('.btn-payment').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.method === method);
    });
}

function setupPaymentMethods() {
    document.querySelectorAll('.btn-payment').forEach(btn => {
        btn.addEventListener('click', () => {
            setPayment(btn.dataset.method);
        });
    });
}

// Sound Beep
function playBeep() {
    if (window.fakeBeep) {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            osc.frequency.value = 800;
            osc.connect(ctx.destination);
            osc.start(); setTimeout(() => osc.stop(), 100);
        } catch (e) { }
    } else {
        audioBeep.currentTime = 0;
        audioBeep.play().catch(e => { window.fakeBeep = true; playBeep(); });
    }
}

// API Calls - Caja
async function checkCajaAbierta() {
    try {
        const res = await fetch('/api/caja/abierta');
        if (res.ok) {
            currentCaja = await res.json();
            updateCajaUI();
        } else {
            Swal.fire('Caja Cerrada', 'Debe abrir caja para poder operar.', 'warning');
        }
    } catch (e) { console.error(e); }
}

function updateCajaUI() {
    const badge = document.getElementById('cajaStatus');
    if (currentCaja) {
        badge.textContent = `Caja Abierta ($${currentCaja.monto_inicial})`;
        badge.classList.replace('danger', 'success');
    } else {
        badge.textContent = 'Caja Cerrada';
        badge.classList.replace('success', 'danger');
    }
}

document.getElementById('btnAbrirCaja').addEventListener('click', async () => {
    if (currentCaja) {
        // Cerrar
        const { value: montoStr } = await Swal.fire({
            title: 'Cerrar Caja',
            input: 'number',
            inputLabel: 'Total Físico en la Caja (Efectivo)',
            inputPlaceholder: '0.00',
            showCancelButton: true
        });
        if (montoStr) {
            const res = await fetch(`/api/caja/${currentCaja.id}/cerrar?monto_final_declarado=${montoStr}`, { method: 'POST' });
            if (res.ok) {
                Swal.fire('Cerrada', 'La caja se cerró exitosamente.', 'success');
                currentCaja = null;
                updateCajaUI();
            }
        }
    } else {
        // Abrir
        const { value: montoStr } = await Swal.fire({
            title: 'Abrir Caja',
            input: 'number',
            inputLabel: 'Monto Inicial',
            inputPlaceholder: '0.00',
            showCancelButton: true
        });
        if (montoStr) {
            const res = await fetch('/api/caja/abrir', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monto_inicial: parseFloat(montoStr) })
            });
            if (res.ok) {
                currentCaja = await res.json();
                updateCajaUI();
                Swal.fire('Éxito', 'Caja abierta.', 'success');
            }
        }
    }
});

// Product Search & Scan
let searchTimeout;
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const q = e.target.value.trim();
    if (q.length < 2) {
        searchResults.classList.add('hidden');
        return;
    }

    searchTimeout = setTimeout(async () => {
        const res = await fetch(`/api/productos/?q=${q}`);
        const items = await res.json();

        searchResults.innerHTML = '';
        if (items.length === 0) {
            searchResults.innerHTML = '<div class="search-item">No encontrado</div>';
        } else {
            // Escáner Rápido (match exacto) -> si el input viene de escáner suele escribir muy rápido y apretar enter
            // But we can eagerly add if exact match
            const exactItem = items.find(i => i.codigo === q);
            if (exactItem && items.length === 1) {
                addToCart(exactItem);
                searchInput.value = '';
                searchResults.classList.add('hidden');
                return;
            }

            items.forEach((it, idx) => {
                const div = document.createElement('div');
                div.className = 'search-item' + (idx === 0 ? ' active' : '');
                div.innerHTML = `<span><strong>${it.codigo}</strong> - ${it.descripcion}</span> <span>$${it.precio.toFixed(2)}</span>`;
                div.addEventListener('click', () => {
                    addToCart(it);
                    searchInput.value = '';
                    searchResults.classList.add('hidden');
                    searchInput.focus();
                });
                searchResults.appendChild(div);
            });
        }
        searchResults.classList.remove('hidden');
    }, 200);
});

// Hide search on blur
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.add('hidden');
    }
    if (!clientInput.contains(e.target) && !clientResults.contains(e.target)) {
        clientResults.classList.add('hidden');
    }
});

// Cart Logic
function addToCart(item) {
    const existing = cart.find(c => c.id === item.id);
    if (existing) {
        existing.cantidad += 1;
    } else {
        cart.push({ ...item, cantidad: 1 });
    }
    playBeep();
    renderCart();
}

function updateCartQty(id, qty) {
    const existing = cart.find(c => c.id === id);
    if (existing) {
        existing.cantidad = parseFloat(qty);
        if (existing.cantidad <= 0) {
            cart = cart.filter(c => c.id !== id);
        }
    }
    renderCart();
}

function removeFromCart(id) {
    cart = cart.filter(c => c.id !== id);
    renderCart();
}

function renderCart() {
    cartBody.innerHTML = '';
    let subtotal = 0;
    cart.forEach(item => {
        const tr = document.createElement('tr');
        const itemSubtotal = item.precio * item.cantidad;
        subtotal += itemSubtotal;

        tr.innerHTML = `
            <td>${item.codigo}</td>
            <td>${item.descripcion}</td>
            <td><input type="number" class="qty-input" value="${item.cantidad}" onchange="updateCartQty(${item.id}, this.value)"></td>
            <td>$${item.precio.toFixed(2)}</td>
            <td>$${itemSubtotal.toFixed(2)}</td>
            <td><button class="btn-icon" onclick="removeFromCart(${item.id})">×</button></td>
        `;
        cartBody.appendChild(tr);
    });

    subtotalDisplay.textContent = `$${subtotal.toFixed(2)}`;
    totalDisplay.textContent = `$${subtotal.toFixed(2)}`; // Without discounts for now
}

// Client Search
let clientTimeout;
clientInput.addEventListener('input', (e) => {
    clearTimeout(clientTimeout);
    const q = e.target.value.trim();
    if (q.length < 2) {
        clientResults.classList.add('hidden');
        clientIdHidden.value = "";
        return;
    }

    clientTimeout = setTimeout(async () => {
        const res = await fetch(`/api/clientes/?q=${q}`);
        const cls = await res.json();

        clientResults.innerHTML = '';
        if (cls.length === 0) {
            clientResults.innerHTML = '<div class="search-item">Sin resultados</div>';
        } else {
            cls.forEach(c => {
                const div = document.createElement('div');
                div.className = 'search-item';
                div.innerHTML = `${c.nombre} (CUIT: ${c.cuit_cuil || '-'})`;
                div.addEventListener('click', () => {
                    clientInput.value = c.nombre;
                    clientIdHidden.value = c.id;
                    clientResults.classList.add('hidden');
                });
                clientResults.appendChild(div);
            });
        }
        clientResults.classList.remove('hidden');
    }, 300);
});

// Consumidor Final quick button
document.getElementById('btnConsumidorFinal').addEventListener('click', () => {
    clientInput.value = 'Consumidor Final';
    clientIdHidden.value = '';
    clientResults.classList.add('hidden');
});

// Checkout process
document.getElementById('btnCancelar').addEventListener('click', () => {
    cart = [];
    clientInput.value = '';
    clientIdHidden.value = '';
    setPayment('efectivo');
    renderCart();
    searchInput.focus();
});

function getCartTotal() {
    return cart.reduce((acc, curr) => acc + (curr.precio * curr.cantidad), 0);
}

document.getElementById('btnCobrar').addEventListener('click', () => {
    if (!currentCaja) {
        Swal.fire('Error', 'Debes abrir caja para cobrar.', 'error');
        return;
    }
    if (cart.length === 0) {
        Swal.fire('Error', 'El carrito está vacío.', 'error');
        return;
    }

    const total = getCartTotal();

    if (selectedPaymentMethod === 'efectivo') {
        document.getElementById('modalTotal').textContent = `$${total.toFixed(2)}`;
        document.getElementById('montoEntregado').value = '';
        document.getElementById('modalVuelto').textContent = '$0.00';
        document.getElementById('modalCobro').classList.remove('hidden');
        setTimeout(() => document.getElementById('montoEntregado').focus(), 100);
    } else {
        procesarVentaGral(); // For other methods, process directly
    }
});

// Modal Logic
function setupModals() {
    document.getElementById('montoEntregado').addEventListener('input', (e) => {
        const entregado = parseFloat(e.target.value) || 0;
        const total = getCartTotal();
        const vuelto = entregado - total;
        document.getElementById('modalVuelto').textContent = `$${vuelto > 0 ? vuelto.toFixed(2) : '0.00'}`;
    });

    document.getElementById('btnConfirmarCobro').addEventListener('click', procesarVentaGral);
    document.getElementById('btnCerrarModal').addEventListener('click', () => {
        document.getElementById('modalCobro').classList.add('hidden');
    });
}

async function procesarVentaGral() {
    const total = getCartTotal();

    const ventaPayload = {
        caja_id: currentCaja.id,
        cliente_id: clientIdHidden.value ? parseInt(clientIdHidden.value) : null,
        subtotal: total,
        descuento_total: 0,
        total: total,
        medio_pago: selectedPaymentMethod,
        detalles: cart.map(i => ({
            item_id: i.id,
            cantidad: i.cantidad,
            precio_unitario: i.precio
        }))
    };

    try {
        const res = await fetch('/api/ventas/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ventaPayload)
        });

        if (res.ok) {
            Swal.fire({
                title: '¡Venta Registrada!',
                text: 'La operación fue exitosa',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false
            });
            document.getElementById('btnCancelar').click(); // Reset all
            document.getElementById('modalCobro').classList.add('hidden');
        } else {
            const err = await res.json();
            Swal.fire('Error', err.detail || 'No se pudo procesar', 'error');
        }
    } catch (e) { console.error(e); }
}
