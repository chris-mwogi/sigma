# Sigma Frontend - Component Development Guide

Guide for creating and maintaining Vue components in the Sigma frontend.

## Component Structure

### Basic Component Template

```vue
<template>
  <div class="component-name">
    <!-- Component content -->
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ComponentName',
  props: {
    // Define component props
  },
  emits: ['event-name'],
  setup(props, { emit }) {
    // Reactive state
    const state = ref('')
    
    // Computed properties
    const computed_value = computed(() => {
      return state.value.toUpperCase()
    })
    
    // Methods
    const handleClick = () => {
      emit('event-name', state.value)
    }
    
    // Lifecycle hooks
    onMounted(() => {
      // Initialize component
    })
    
    return {
      state,
      computed_value,
      handleClick
    }
  }
}
</script>

<style scoped>
.component-name {
  /* Component styles */
}
</style>
```

## Component Types

### 1. Page Components (Views)

Located in `src/views/`, these are full-page components.

**Example: Dashboard.vue**
- Fetch data on mount
- Display multiple sections
- Handle user interactions
- Navigate to other pages

### 2. Reusable Components

Located in `src/components/`, these are used across multiple pages.

**Example: DataTable.vue**
- Accept data as props
- Emit events for user actions
- Be self-contained
- Have clear prop/event contracts

### 3. Layout Components

Provide structure for pages.

**Example: Card.vue**
```vue
<template>
  <div class="card">
    <div v-if="$slots.header" class="card-header">
      <slot name="header"></slot>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>
```

## Best Practices

### 1. Props Definition

Always define props with types:

```javascript
props: {
  title: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
}
```

### 2. Event Emission

Use descriptive event names:

```javascript
emits: ['item-selected', 'delete-item', 'update-item']

// Emit with data
emit('item-selected', item)
```

### 3. Composition API

Use Composition API for better code organization:

```javascript
import { ref, computed, onMounted } from 'vue'

setup(props, { emit }) {
  const items = ref([])
  
  const filteredItems = computed(() => {
    return items.value.filter(item => item.active)
  })
  
  onMounted(() => {
    loadItems()
  })
  
  return { items, filteredItems }
}
```

### 4. Scoped Styles

Always use scoped styles to avoid conflicts:

```vue
<style scoped>
.component-name {
  /* Styles only apply to this component */
}
</style>
```

### 5. Error Handling

Handle errors gracefully:

```javascript
const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/endpoint')
    data.value = response.data
  } catch (err) {
    error.value = err.message || 'Failed to load data'
  } finally {
    loading.value = false
  }
}
```

## Common Patterns

### Data Loading

```javascript
const loading = ref(false)
const data = ref([])
const error = ref('')

const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/api/resource/DocType')
    data.value = response.data.data || []
  } catch (err) {
    error.value = err.response?.data?.message || 'Error loading data'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
```

### Search and Filter

```javascript
const searchQuery = ref('')
const filterValue = ref('')

const filteredData = computed(() => {
  let filtered = data.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(query) ||
      item.title.toLowerCase().includes(query)
    )
  }
  
  if (filterValue.value) {
    filtered = filtered.filter(item => item.status === filterValue.value)
  }
  
  return filtered
})
```

### Pagination

```javascript
const currentPage = ref(1)
const pageSize = ref(10)

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / pageSize.value)
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})
```

### Form Handling

```javascript
const form = ref({
  title: '',
  description: '',
  status: 'Open'
})

const submitForm = async () => {
  error.value = ''
  
  if (!form.value.title.trim()) {
    error.value = 'Title is required'
    return
  }
  
  loading.value = true
  try {
    const response = await api.post('/api/resource/DocType', form.value)
    success.value = 'Created successfully'
    // Reset form
    form.value = { title: '', description: '', status: 'Open' }
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to save'
  } finally {
    loading.value = false
  }
}
```

## Styling Guidelines

### Use CSS Variables

```css
:root {
  --primary-color: #0084ff;
  --secondary-color: #1a1a1a;
  --success-color: #28a745;
  --danger-color: #dc3545;
}

.button {
  background-color: var(--primary-color);
}
```

### Responsive Design

```css
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  .navbar {
    flex-direction: column;
  }
}
```

### Utility Classes

Use utility classes from `main.css`:

```html
<div class="flex-between mb-3 p-2">
  <h1>Title</h1>
  <button class="btn btn-primary">Action</button>
</div>
```

## Testing Components

### Unit Test Example

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from './MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: { title: 'Test' }
    })
    expect(wrapper.text()).toContain('Test')
  })
  
  it('emits event on click', async () => {
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

## Performance Tips

1. **Lazy Load Components**
```javascript
const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
)
```

2. **Memoize Computed Properties**
```javascript
const expensiveComputation = computed(() => {
  // Only recalculates when dependencies change
  return complexCalculation(data.value)
})
```

3. **Debounce Search**
```javascript
import { debounce } from 'lodash-es'

const handleSearch = debounce((query) => {
  searchQuery.value = query
}, 300)
```

4. **Virtual Scrolling for Large Lists**
Use `vue-virtual-scroller` for lists with 1000+ items.

## Accessibility

- Use semantic HTML
- Add ARIA labels
- Ensure keyboard navigation
- Maintain color contrast
- Provide alt text for images

```vue
<button 
  @click="handleClick"
  aria-label="Delete item"
  :disabled="loading"
>
  Delete
</button>
```

## Common Mistakes to Avoid

1. ❌ Mutating props directly
   - ✅ Use `emit` to notify parent

2. ❌ Not handling loading/error states
   - ✅ Always show loading and error UI

3. ❌ Hardcoding strings
   - ✅ Use constants or props

4. ❌ Not cleaning up subscriptions
   - ✅ Use `onUnmounted` to clean up

5. ❌ Mixing concerns in components
   - ✅ Separate logic into services/stores

## Resources

- Vue 3 Docs: https://vuejs.org
- Composition API: https://vuejs.org/guide/extras/composition-api-faq.html
- Best Practices: https://vuejs.org/guide/best-practices/

## Support

For component development questions:
- Review existing components
- Check Vue documentation
- Contact: info@prismod.co.ke

