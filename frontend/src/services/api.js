
const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
).replace(/\/+$/, '')

// ========================================
// CSRF TOKEN
// ========================================

async function getCsrfToken() {
    const response = await fetch(`${API_BASE_URL}/auth/csrf/`, {
        method: 'GET',
        credentials: 'include',
    })

    if (!response.ok) {
        throw new Error('Unable to get CSRF token.')
    }

    const data = await response.json()
    return data.csrfToken || data.csrf_token || ''
}

// ========================================
// COMMON API REQUEST
// ========================================

async function apiRequest(endpoint, options = {}) {
    const method = (options.method || 'GET').toUpperCase()
    const headers = new Headers(options.headers || {})

    // Automatically attach a CSRF token to state-changing requests.
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const csrfToken = await getCsrfToken()

        if (csrfToken) {
            headers.set('X-CSRFToken', csrfToken)
        }
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        method,
        credentials: 'include',
        headers,
    })

    if (response.status === 204) {
        return null
    }

    const contentType = response.headers.get('content-type') || ''
    let data = null

    if (contentType.includes('application/json')) {
        data = await response.json()
    } else {
        data = await response.text()
    }

    if (!response.ok) {
        let message = `Request failed (${response.status}).`

        if (typeof data === 'string' && data) {
            message = data
        } else if (data && typeof data === 'object') {
            message = Object.entries(data)
                .map(([key, value]) => {
                    const text = Array.isArray(value)
                        ? value.join(' ')
                        : typeof value === 'object' && value !== null
                            ? JSON.stringify(value)
                            : String(value)

                    return key === 'detail' || key === 'message'
                        ? text
                        : `${key}: ${text}`
                })
                .join(' ')
        }

        throw new Error(message)
    }

    return data
}

// ========================================
// COMPONENTS
// ========================================

export async function getComponents() {
    return apiRequest('/components/')
}

export async function getComponent(componentId) {
    return apiRequest(`/components/${componentId}/`)
}

export async function createComponent(componentData) {
    const isFormData = componentData instanceof FormData
    const headers = {}

    if (!isFormData) {
        headers['Content-Type'] = 'application/json'
    }

    return apiRequest('/components/', {
        method: 'POST',
        headers,
        body: isFormData
            ? componentData
            : JSON.stringify(componentData),
    })
}

export async function updateComponent(componentId, componentData) {
    const isFormData = componentData instanceof FormData
    const headers = {}

    if (!isFormData) {
        headers['Content-Type'] = 'application/json'
    }

    return apiRequest(`/components/${componentId}/`, {
        method: 'PATCH',
        headers,
        body: isFormData
            ? componentData
            : JSON.stringify(componentData),
    })
}

export async function deleteComponent(componentId) {
    return apiRequest(`/components/${componentId}/`, {
        method: 'DELETE',
    })
}

// ========================================
// AUTHENTICATION
// ========================================

export async function loginUser(username, password) {
    return apiRequest('/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username,
            password,
        }),
    })
}

export async function logoutUser() {
    return apiRequest('/auth/logout/', {
        method: 'POST',
    })
}

export async function getCurrentUser() {
    return apiRequest('/auth/me/')
}

export async function registerUser(userData) {
    return apiRequest('/auth/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
}

// ========================================
// CART
// ========================================

export async function getCartItems() {
    return apiRequest('/cart/')
}

export async function addToCart(componentId, quantity = 1) {
    return apiRequest('/cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            component: componentId,
            quantity,
        }),
    })
}

export async function updateCartItemQuantity(cartItemId, quantity) {
    return apiRequest(`/cart/${cartItemId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            quantity,
        }),
    })
}

export async function removeCartItem(cartItemId) {
    return apiRequest(`/cart/${cartItemId}/`, {
        method: 'DELETE',
    })
}

export async function checkoutCart(paymentMethod = 'cod') {
    return apiRequest('/cart/checkout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            payment_method: paymentMethod,
        }),
    })
}

// ========================================
// MY ORDERS
// ========================================

export async function getMyOrders() {
    return apiRequest('/cart/my-orders/')
}

// ========================================
// ADMIN ORDER MANAGEMENT
// ========================================

export async function getAdminOrders() {
    return apiRequest('/cart/admin-orders/')
}

export async function updateAdminOrderStatus(orderId, newStatus) {
    return apiRequest(`/cart/admin-orders/${orderId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: newStatus,
        }),
    })
}
