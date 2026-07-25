export const INCOME_CATEGORIES = [
  { value: 'salary', label: 'Salary', icon: 'salary', color: '#0072CE' },
  { value: 'bonus', label: 'Bonus', icon: 'bonus', color: '#F5822A' },
  { value: 'allowance', label: 'Allowance', icon: 'allowance', color: '#00B14F' },
  { value: 'interest', label: 'Interest', icon: 'interest', color: '#00378E' },
  { value: 'investment', label: 'Investment', icon: 'investment', color: '#1E9E6B' },
  { value: 'cashback', label: 'Cashback', icon: 'cashback', color: '#7B2FF7' },
  { value: 'other', label: 'Other', icon: 'other', color: '#5A6178' },
]

const CATEGORY_BY_VALUE = new Map(INCOME_CATEGORIES.map((c) => [c.value, c]))

export function incomeCategory(value) {
  return CATEGORY_BY_VALUE.get(value) || { value, label: 'Other', icon: 'other', color: '#5A6178' }
}
