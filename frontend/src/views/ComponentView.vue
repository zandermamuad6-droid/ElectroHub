
<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  getComponents,
  createComponent,
  updateComponent,
  deleteComponent,
} from '../services/api'

const components = ref([])
const searchQuery = ref('')

const filteredComponents = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) return components.value

  return components.value.filter((component) =>
      String(component.name || '').toLowerCase().includes(query)
  )
})
const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const editingId = ref(null)
const errorMessage = ref('')
const successMessage = ref('')
const selectedImage = ref(null)
const imagePreview = ref('')

const emptyForm = () => ({
  name: '',
  quantity: 0,
  price: '',
})

const form = ref(emptyForm())

const totalValue = (component) =>
    Number(component.quantity || 0) * Number(component.price || 0)

const formatPrice = (value) =>
    Number(value || 0).toLocaleString('en-PH', {
      style: 'currency',
      currency: 'PHP',
    })

async function loadComponents() {
  loading.value = true
  errorMessage.value = ''

  try {
    const data = await getComponents()
    components.value = Array.isArray(data) ? data : data.results || []
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load components.'
  } finally {
    loading.value = false
  }
}

function clearImagePreview() {
  if (imagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreview.value)
  }

  imagePreview.value = ''
  selectedImage.value = null

  const input = document.getElementById('component-image')
  if (input) input.value = ''
}

function resetForm() {
  clearImagePreview()
  form.value = emptyForm()
  editingId.value = null
  errorMessage.value = ''
}

function toggleForm() {
  if (showForm.value) {
    showForm.value = false
    resetForm()
    successMessage.value = ''
    return
  }

  resetForm()
  successMessage.value = ''
  showForm.value = true
}

function editComponent(component) {
  resetForm()
  successMessage.value = ''
  errorMessage.value = ''

  editingId.value = component.id
  form.value = {
    name: component.name,
    quantity: Number(component.quantity),
    price: component.price,
  }

  imagePreview.value = component.image_url || ''
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleImageChange(event) {
  const file = event.target.files?.[0]

  if (!file) return

  if (!file.type.startsWith('image/')) {
    errorMessage.value = 'Please select a valid image file.'
    event.target.value = ''
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    errorMessage.value = 'Image size must not exceed 5 MB.'
    event.target.value = ''
    return
  }

  if (imagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreview.value)
  }

  selectedImage.value = file
  imagePreview.value = URL.createObjectURL(file)
  errorMessage.value = ''
}

async function saveComponent() {
  errorMessage.value = ''
  successMessage.value = ''

  const name = form.value.name.trim()
  const quantity = Number(form.value.quantity)
  const price = Number(form.value.price)

  if (!name) {
    errorMessage.value = 'Please enter the component name.'
    return
  }

  if (
      form.value.quantity === '' ||
      !Number.isInteger(quantity) ||
      quantity < 0
  ) {
    errorMessage.value = 'Quantity must be a whole number of 0 or higher.'
    return
  }

  if (
      form.value.price === '' ||
      !Number.isFinite(price) ||
      price < 0
  ) {
    errorMessage.value = 'Price must be 0 or higher.'
    return
  }

  saving.value = true

  try {
    let payload

    if (selectedImage.value) {
      payload = new FormData()
      payload.append('name', name)
      payload.append('quantity', String(quantity))
      payload.append('price', price.toFixed(2))
      payload.append('image', selectedImage.value)
    } else {
      payload = {
        name,
        quantity,
        price: price.toFixed(2),
      }
    }

    if (editingId.value !== null) {
      await updateComponent(editingId.value, payload)
      successMessage.value = 'Component updated successfully!'
    } else {
      await createComponent(payload)
      successMessage.value = 'Component added successfully!'
    }

    resetForm()
    showForm.value = false
    await loadComponents()
    errorMessage.value = ''
  } catch (error) {
    errorMessage.value = error.message || 'Unable to save component.'
  } finally {
    saving.value = false
  }
}

async function removeComponent(component) {
  const confirmed = window.confirm(
      `Are you sure you want to delete "${component.name}"? This action cannot be undone.`,
  )

  if (!confirmed) return

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await deleteComponent(component.id)

    components.value = components.value.filter(
        (item) => item.id !== component.id,
    )

    successMessage.value = `${component.name} deleted successfully!`
  } catch (error) {
    errorMessage.value = error.message || 'Unable to delete component.'
  }
}

onMounted(loadComponents)
onBeforeUnmount(() => {
  if (imagePreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreview.value)
  }
})
</script>

<template>
  <div class="components-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">INVENTORY MANAGEMENT</p>
        <h1>Components</h1>
        <p class="subtitle">Manage your electronic components and stock.</p>
      </div>

      <button class="primary-button" @click="toggleForm">
        {{ showForm ? 'Cancel' : '+ Add Component' }}
      </button>
    </header>

    <div v-if="successMessage" class="message success-message">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </div>

    <section v-if="showForm" class="form-card">
      <div class="form-heading">
        <h2>{{ editingId !== null ? 'Edit Component' : 'Add Component' }}</h2>
        <p>
          {{
            editingId !== null
                ? 'Update the component information below.'
                : 'Enter the details of your new component.'
          }}
        </p>
      </div>

      <form class="component-form" @submit.prevent="saveComponent">
        <div class="form-group">
          <label for="component-name">Component Name</label>
          <input
              id="component-name"
              v-model="form.name"
              type="text"
              placeholder="e.g. Resistor 220Ω"
              maxlength="150"
              required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="component-quantity">Quantity</label>
            <input
                id="component-quantity"
                v-model.number="form.quantity"
                type="number"
                min="0"
                step="1"
                required
            />
          </div>

          <div class="form-group">
            <label for="component-price">Unit Price (₱)</label>
            <input
                id="component-price"
                v-model="form.price"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="component-image">Component Image</label>
          <input
              id="component-image"
              type="file"
              accept="image/*"
              @change="handleImageChange"
          />
          <small>Choose an image file. Maximum size: 5 MB.</small>

          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Component image preview" />
            <button
                type="button"
                class="secondary-button"
                @click="clearImagePreview"
            >
              Remove selected image
            </button>
          </div>
        </div>

        <div class="form-actions">
          <button
              type="button"
              class="secondary-button"
              @click="toggleForm"
          >
            Cancel
          </button>

          <button
              type="submit"
              class="primary-button"
              :disabled="saving"
          >
            {{
              saving
                  ? 'Saving...'
                  : editingId !== null
                      ? 'Update Component'
                      : 'Save Component'
            }}
          </button>
        </div>
      </form>
    </section>

    <section class="table-card">
      <div class="table-heading">
        <div>
          <h2>Component Inventory</h2>
          <p>All registered electronic components</p>
        </div>

        <span class="count-badge">
          {{ filteredComponents.length }}
          {{ filteredComponents.length === 1 ? 'item' : 'items' }}
        </span>
      </div>

      <div class="search-wrapper">
        <input
            id="component-search"
            v-model="searchQuery"
            type="search"
            placeholder="Search components by name..."
            autocomplete="off"
            aria-label="Search components by name"
        />
      </div>

      <div v-if="loading" class="empty-state">
        Loading components...
      </div>

      <div v-else-if="components.length === 0" class="empty-state">
        <h3>No components yet</h3>
        <p>Click “Add Component” to add your first inventory item.</p>
      </div>

      <div v-else-if="filteredComponents.length === 0" class="empty-state">
        <h3>No matching components</h3>
        <p>Try searching with a different component name.</p>
      </div>

      <div v-else class="table-wrapper">
        <table>
          <thead>
          <tr>
            <th>Image</th>
            <th>Component Name</th>
            <th>Quantity</th>
            <th>Unit Price</th>
            <th>Total Value</th>
            <th>Actions</th>
          </tr>
          </thead>

          <tbody>
          <tr v-for="component in filteredComponents" :key="component.id">
            <td>
              <img
                  v-if="component.image_url"
                  :src="component.image_url"
                  :alt="component.name"
                  class="component-thumbnail"
              />
              <span v-else class="no-image">No image</span>
            </td>
            <td class="component-name">{{ component.name }}</td>
            <td>{{ component.quantity }}</td>
            <td>{{ formatPrice(component.price) }}</td>
            <td class="total-value">
              {{ formatPrice(totalValue(component)) }}
            </td>
            <td>
              <div class="action-buttons">
                <button
                    class="edit-button"
                    type="button"
                    @click="editComponent(component)"
                >
                  Edit
                </button>

                <button
                    class="delete-button"
                    type="button"
                    @click="removeComponent(component)"
                >
                  Delete
                </button>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.components-page {
  padding: 32px;
  color: #252344;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #7863d8;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.5px;
}

.page-header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
}

.subtitle {
  margin: 8px 0 0;
  color: #77758e;
}

.primary-button,
.secondary-button,
.edit-button,
.delete-button {
  border: none;
  border-radius: 9px;
  padding: 11px 17px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.primary-button {
  background: #7257d9;
  color: white;
}

.primary-button:hover {
  background: #6044c5;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-button {
  background: #f0eef8;
  color: #514a73;
}

.form-card,
.table-card {
  margin-bottom: 24px;
  padding: 25px;
  border: 1px solid #ebe8f5;
  border-radius: 16px;
  background: white;
  box-shadow: 0 5px 20px rgb(43 31 91 / 4%);
}

.form-heading h2,
.table-heading h2 {
  margin: 0;
  font-size: 19px;
}

.form-heading p,
.table-heading p {
  margin: 7px 0 0;
  color: #85829a;
  font-size: 13px;
}

.component-form {
  margin-top: 23px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 18px;
}

.form-group label {
  color: #494660;
  font-size: 13px;
  font-weight: 700;
}

.form-group input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1px solid #dedbea;
  border-radius: 9px;
  outline: none;
  color: #252344;
  background: #fff;
}

.form-group input:focus {
  border-color: #8068e2;
  box-shadow: 0 0 0 3px rgb(128 104 226 / 12%);
}

.form-group small {
  color: #85829a;
  font-size: 12px;
}

.image-preview {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 12px;
}

.image-preview img {
  width: 150px;
  height: 120px;
  object-fit: contain;
  border: 1px solid #ebe8f5;
  border-radius: 10px;
  background: #f8f7fc;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.table-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
}

.count-badge {
  padding: 7px 12px;
  border-radius: 20px;
  background: #f0edff;
  color: #7257d9;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.search-wrapper {
  margin-bottom: 20px;
}

.search-wrapper input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 15px;
  border: 1px solid #dedbea;
  border-radius: 10px;
  outline: none;
  color: #252344;
  background: #fff;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-wrapper input:focus {
  border-color: #8068e2;
  box-shadow: 0 0 0 3px rgb(128 104 226 / 12%);
}

.search-wrapper input::placeholder {
  color: #a09cb3;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead {
  background: #f8f7fc;
}

th {
  padding: 14px;
  color: #77738f;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

td {
  padding: 16px 14px;
  border-bottom: 1px solid #f0eef6;
  color: #5e5a75;
  font-size: 13px;
}

tbody tr:last-child td {
  border-bottom: none;
}

.component-name {
  color: #302b4e;
  font-weight: 700;
}

.total-value {
  color: #5c46b8;
  font-weight: 800;
}

.component-thumbnail {
  width: 58px;
  height: 48px;
  object-fit: contain;
  border: 1px solid #ebe8f5;
  border-radius: 8px;
  background: #f8f7fc;
}

.no-image {
  color: #a09caf;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-button,
.delete-button {
  padding: 8px 11px;
  font-size: 12px;
}

.edit-button {
  background: #eeeaff;
  color: #674cc6;
}

.edit-button:hover {
  background: #ded5ff;
}

.delete-button {
  background: #fff0f0;
  color: #cc4545;
}

.delete-button:hover {
  background: #ffe0e0;
}

.empty-state {
  padding: 35px 15px;
  color: #85829a;
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: #494660;
}

.empty-state p {
  margin: 0;
  font-size: 13px;
}

.message {
  margin-bottom: 18px;
  padding: 13px 16px;
  border-radius: 9px;
  font-size: 13px;
}

.success-message {
  border: 1px solid #b9e8cc;
  background: #effbf3;
  color: #207344;
}

.error-message {
  border: 1px solid #f1caca;
  background: #fff1f1;
  color: #b52f2f;
}

@media (max-width: 700px) {
  .components-page {
    padding: 18px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .form-card,
  .table-card {
    padding: 17px;
  }
}
</style>
