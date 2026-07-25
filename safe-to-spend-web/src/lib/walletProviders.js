// Official provider logos (trademarks of their respective owners, used here
// solely to help users identify their own accounts). `color`/`initials` stay
// as a fallback for any provider without a logo asset.

import gcash from '@/assets/wallets/gcash.svg'
import maya from '@/assets/wallets/maya.svg'
import shopeepay from '@/assets/wallets/shopeepay.png'
import grabpay from '@/assets/wallets/grabpay.png'
import coinsph from '@/assets/wallets/coinsph.png'

import maribank from '@/assets/wallets/maribank.png'
import gotyme from '@/assets/wallets/gotyme.svg'
import tonik from '@/assets/wallets/tonik.svg'
import unobank from '@/assets/wallets/unobank.png'

import bdo from '@/assets/wallets/bdo.svg'
import bpi from '@/assets/wallets/bpi.svg'
import metrobank from '@/assets/wallets/metrobank.svg'
import landbank from '@/assets/wallets/landbank.svg'
import pnb from '@/assets/wallets/pnb.svg'
import securitybank from '@/assets/wallets/securitybank.svg'
import unionbank from '@/assets/wallets/unionbank.svg'
import rcbc from '@/assets/wallets/rcbc.svg'

export const WALLET_GROUPS = [
  {
    kind: 'ewallet',
    label: 'E-Wallets',
    providers: [
      { name: 'GCash', initials: 'GC', color: '#0072CE', logo: gcash },
      { name: 'Maya', initials: 'M', color: '#00B87C', logo: maya },
      { name: 'ShopeePay', initials: 'SP', color: '#EE4D2D', logo: shopeepay },
      { name: 'GrabPay', initials: 'GP', color: '#00B14F', logo: grabpay },
      { name: 'Coins.ph', initials: 'C', color: '#1BA0E2', logo: coinsph },
    ],
  },
  {
    kind: 'digital_bank',
    label: 'Digital Banks',
    providers: [
      { name: 'MariBank', initials: 'MB', color: '#6C2EB5', logo: maribank },
      { name: 'GoTyme', initials: 'GT', color: '#7B2FF7', logo: gotyme },
      { name: 'Tonik', initials: 'T', color: '#0A2540', logo: tonik },
      { name: 'UNObank', initials: 'U', color: '#F5822A', logo: unobank },
    ],
  },
  {
    kind: 'bank',
    label: 'Banks',
    providers: [
      { name: 'BDO', initials: 'BDO', color: '#00378E', logo: bdo },
      { name: 'BPI', initials: 'BPI', color: '#B9202D', logo: bpi },
      { name: 'Metrobank', initials: 'MB', color: '#00397B', logo: metrobank },
      { name: 'Landbank', initials: 'LB', color: '#00693E', logo: landbank },
      { name: 'PNB', initials: 'PNB', color: '#F5821F', logo: pnb },
      { name: 'Security Bank', initials: 'SB', color: '#E4002B', logo: securitybank },
      { name: 'UnionBank', initials: 'UB', color: '#F7941D', logo: unionbank },
      { name: 'RCBC', initials: 'R', color: '#00539F', logo: rcbc },
    ],
  },
  {
    kind: 'cash',
    label: 'Cash',
    providers: [
      { name: 'Cash', initials: '₱', color: '#1E9E6B', icon: 'cash' },
      { name: 'Wallet', initials: 'W', color: '#00A19A', icon: 'wallet' },
      { name: 'Piggy Bank', initials: 'PB', color: '#E0559C', icon: 'piggy_bank' },
      { name: 'Petty Cash', initials: 'PC', color: '#8A5A3B', icon: 'petty_cash' },
    ],
  },
]

export const KIND_LABEL = {
  ewallet: 'E-Wallet',
  digital_bank: 'Digital Bank',
  bank: 'Bank',
  cash: 'Cash',
}

const PROVIDER_BY_NAME = new Map(
  WALLET_GROUPS.flatMap((group) => group.providers.map((p) => [p.name, p])),
)

export function providerIcon(name) {
  return PROVIDER_BY_NAME.get(name) || { name, initials: name?.[0]?.toUpperCase() || '?', color: '#5A6178' }
}
