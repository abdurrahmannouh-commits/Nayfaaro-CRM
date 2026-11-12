import { createDocumentResource } from 'frappe-ui'
import { reactive, ref } from 'vue'

const settings = ref({})
const brand = reactive({
  name: 'Nayfaaro CRM',
  logo: '',
  favicon: '/assets/crm/images/logo.svg',
})

const _settings = createDocumentResource({
  doctype: 'FCRM Settings',
  name: 'FCRM Settings',
  onSuccess: (data) => {
    settings.value = data
    getSettings().setupBrand()
    return data
  },
})

export function getSettings() {
  function setupBrand() {
    brand.name = settings.value?.brand_name || 'Nayfaaro CRM'
    brand.logo = settings.value?.brand_logo || ''
    brand.favicon = settings.value?.favicon || '/assets/crm/images/logo.svg'

    if (typeof document !== 'undefined' && brand.favicon) {
      let link = document.querySelector("link[rel*='icon']")
      if (!link) {
        link = document.createElement('link')
        link.rel = 'icon'
        document.head.appendChild(link)
      }
      link.href = brand.favicon
    }
  }

  return {
    _settings,
    settings,
    brand,
    setupBrand,
  }
}
