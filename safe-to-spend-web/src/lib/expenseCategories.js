export const EXPENSE_GROUPS = [
  {
    kind: 'everyday',
    label: 'Everyday',
    items: [
      { value: 'food', label: 'Food & Dining', icon: 'food', color: '#E08A1E' },
      { value: 'groceries', label: 'Groceries', icon: 'groceries', color: '#00B14F' },
      { value: 'transpo', label: 'Transport', icon: 'transpo', color: '#0072CE' },
      { value: 'shopping', label: 'Shopping', icon: 'shopping', color: '#B9202D' },
    ],
  },
  {
    kind: 'living',
    label: 'Living',
    items: [
      { value: 'bills', label: 'Bills & Utilities', icon: 'bills', color: '#6C2EB5' },
      { value: 'home', label: 'Home', icon: 'home', color: '#00378E' },
      { value: 'health', label: 'Health & Wellness', icon: 'health', color: '#D6473C' },
      { value: 'subscriptions', label: 'Subscriptions', icon: 'subscriptions', color: '#7B2FF7' },
    ],
  },
  {
    kind: 'lifestyle',
    label: 'Lifestyle',
    items: [
      { value: 'entertainment', label: 'Entertainment', icon: 'entertainment', color: '#0E9AA6' },
      { value: 'games', label: 'Games', icon: 'games', color: '#5B4FE8' },
      { value: 'travel', label: 'Travel', icon: 'travel', color: '#1E9E6B' },
      { value: 'personal_care', label: 'Personal Care', icon: 'personal_care', color: '#E0559C' },
      { value: 'pets', label: 'Pets', icon: 'pets', color: '#8A5A3B' },
      { value: 'education', label: 'Education', icon: 'education', color: '#00A19A' },
      { value: 'tithes', label: 'Tithes & Offering', icon: 'tithes', color: '#C9962C' },
      { value: 'gifts', label: 'Gifts', icon: 'gifts', color: '#F5822A' },
    ],
  },
  {
    kind: 'other',
    label: 'Other',
    items: [{ value: 'other', label: 'Other', icon: 'other', color: '#5A6178' }],
  },
]

export const EXPENSE_CATEGORIES = EXPENSE_GROUPS.flatMap((group) => group.items)

const CATEGORY_BY_VALUE = new Map(EXPENSE_CATEGORIES.map((c) => [c.value, c]))

export function expenseCategory(value) {
  return CATEGORY_BY_VALUE.get(value) || { value, label: 'Other', icon: 'other', color: '#5A6178' }
}
