<script setup>
import { ref, useId } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Password' },
  placeholder: { type: String, default: '••••••••' },
  autocomplete: { type: String, default: 'current-password' },
  minlength: { type: [String, Number], default: null },
})

defineEmits(['update:modelValue'])

const inputId = useId()
const visible = ref(false)
</script>

<template>
  <label :for="inputId" class="flex flex-col gap-1.5 text-sm font-semibold">
    {{ label }}
    <span class="relative flex items-stretch">
      <input
        :id="inputId"
        :value="modelValue"
        :type="visible ? 'text' : 'password'"
        required
        :minlength="minlength || undefined"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        class="w-full min-w-0 rounded-xl border border-border bg-bg-sunken py-2.5 pl-3.5 pr-11 text-sm font-normal outline-none focus:border-accent"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <button
        type="button"
        class="absolute inset-y-0 right-0 flex w-11 shrink-0 items-center justify-center text-text-dim transition hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        :aria-label="visible ? 'Hide password' : 'Show password'"
        :aria-pressed="visible"
        tabindex="-1"
        @click="visible = !visible"
      >
        <svg v-if="visible" width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M3 3l18 18M10.6 10.7a2.5 2.5 0 0 0 3.5 3.5M9.4 5.5A10.6 10.6 0 0 1 12 5c5.5 0 9 5 9.9 7-.4.9-1.2 2.2-2.4 3.4M6.6 6.6C4.5 8 3 10 2.1 12c1 2.3 3.4 6 9.9 7 1.2 0 2.4-.2 3.4-.6"
            stroke="currentColor"
            stroke-width="1.7"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path
            d="M2.1 12c1-2.3 4.5-7 9.9-7s8.9 4.7 9.9 7c-1 2.3-4.5 7-9.9 7s-8.9-4.7-9.9-7Z"
            stroke="currentColor"
            stroke-width="1.7"
            stroke-linejoin="round"
          />
          <circle cx="12" cy="12" r="2.6" stroke="currentColor" stroke-width="1.7" />
        </svg>
      </button>
    </span>
  </label>
</template>
