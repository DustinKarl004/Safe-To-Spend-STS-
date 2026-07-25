export const OBLIGATION_GROUPS = [
  {
    kind: 'housing',
    label: 'Housing',
    items: [
      { name: 'Rent', icon: '🏠', color: '#6C2EB5' },
      { name: 'Mortgage', icon: '🏦', color: '#00378E' },
    ],
  },
  {
    kind: 'utilities',
    label: 'Utilities',
    items: [
      { name: 'Electricity', icon: '💡', color: '#E08A1E' },
      { name: 'Water', icon: '🚰', color: '#0E9AA6' },
      { name: 'Internet', icon: '📶', color: '#0072CE' },
      { name: 'Phone / Load', icon: '📱', color: '#00B14F' },
    ],
  },
  {
    kind: 'debt',
    label: 'Debt & Credit',
    items: [
      { name: 'Credit Card', icon: '💳', color: '#B9202D' },
      { name: 'Loan Payment', icon: '💸', color: '#D6473C' },
    ],
  },
  {
    kind: 'other',
    label: 'Other',
    items: [
      { name: 'Insurance', icon: '🛡️', color: '#1E9E6B' },
      { name: 'Subscription', icon: '🔁', color: '#7B2FF7' },
      { name: 'Tuition', icon: '🎓', color: '#F5822A' },
      { name: 'Other', icon: '📌', color: '#5A6178' },
    ],
  },
]

const CATEGORY_BY_NAME = new Map(
  OBLIGATION_GROUPS.flatMap((group) => group.items.map((item) => [item.name, item])),
)

export function obligationIcon(name) {
  return CATEGORY_BY_NAME.get(name) || { name, icon: '📌', color: '#5A6178' }
}
