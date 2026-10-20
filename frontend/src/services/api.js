
const API_BASE_URL = 'http://localhost:8000/api'

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        credentials: 'include',
        ...options,
        headers: {
            Accept: 'application/json',
            ...options.headers,
        },
    })

    const data = await response.json().catch(() => null)

    if (!response.ok) {
        const detail = data?.detail
            || Object.entries(data || {})
                .map(([key, value]) =>
                    `${key}: ${Array.isArray(value) ? value.join(', ') : value}`,
                )
                .join('; ')

        throw new Error(detail || `Request failed: ${response.status}`)
    }

    return data
}

export async function getCsrfToken() {
    const data = await apiRequest('/auth/csrf/')
    return data.csrfToken
}

export async function loginUser(username, password) {
    const csrfToken = await getCsrfToken()

    const data = await apiRequest('/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ username, password }),
    })

    return data.user
}

export async function getCurrentUser() {
    return apiRequest('/auth/me/')
}

export async function logoutUser() {
    const csrfToken = await getCsrfToken()

    return apiRequest('/auth/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
}

export async function getComponents() {
    return apiRequest('/components/')
}

export async function createComponent(component) {
    const csrfToken = await getCsrfToken()

    const isFormData = component instanceof FormData

    return apiRequest('/components/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            ...(isFormData ? {} : {
                'Content-Type': 'application/json',
            }),
        },
        body: isFormData
            ? component
            : JSON.stringify(component),
    })
}

export async function updateComponent(id, component) {
    const csrfToken = await getCsrfToken()

    const isFormData = component instanceof FormData

    return apiRequest(`/components/${id}/`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrfToken,
            ...(isFormData ? {} : {
                'Content-Type': 'application/json',
            }),
        },
        body: isFormData
            ? component
            : JSON.stringify(component),
    })
}

export async function deleteComponent(id) {
    const csrfToken = await getCsrfToken()

    return apiRequest(`/components/${id}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
}
