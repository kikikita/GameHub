import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    topbar: {
      realms: 'Realms',
      story: 'Story',
      settings: 'Settings',
      plan: 'Plan',
      store: 'Store',
    },
    settings: {
      yourPlan: 'Your plan',
      language: 'Language',
      free: 'Free',
      pro: 'PRO⚡',
      upgrade: 'Upgrade',
    },
    planUpgrade: {
      infiniteEnergy: 'Infinite energy',
      wishesForShopping: '{{count}} wishes for bringing your ideas to life',
      mostAdvancedAI: 'Our most advanced AI',
      unlimitedPhotoGeneration: 'Unlimited photo generation',
      nearInstantReplyTimes: 'Near instant reply times',
      upgrade: 'Upgrade',
    },
    store: {
      unlimitedEnergy: 'Unlimited Energy',
      unlimitedEnergyDescription: 'Remove the barriers. Gain endless energy!',
      recharge: 'Recharge',
      wishes: 'Wishes',
    },
  },
  ru: {
    topbar: {
      realms: 'Миры',
      story: 'История',
      settings: 'Настройки',
      plan: 'План',
      store: 'Магазин',
    },
    settings: {
      yourPlan: 'Ваш план',
      language: 'Язык',
      free: 'Бесплатный',
      pro: 'PRO⚡',
      upgrade: 'Улучшить',
    },
    planUpgrade: {
      infiniteEnergy: 'Бесконечная энергия',
      wishesForShopping: '{{count}} желаний для реализации своих идей',
      mostAdvancedAI: 'Наш самый продвинутый ИИ',
      unlimitedPhotoGeneration: 'Неограниченная генерация фото',
      nearInstantReplyTimes: 'Быстрые ответы',
      upgrade: 'Улучшить',
    },
    store: {
      unlimitedEnergy: 'Бесконечная энергия',
      unlimitedEnergyDescription: 'Снимите ограничения. Получите бесконечную энергию!',
      recharge: 'Пополнить',
      wishes: 'Желаний',
    },
  },
} as const;

const storedLng = localStorage.getItem('language') || 'en';

i18n.use(initReactI18next).init({
  resources,
  lng: storedLng,
  fallbackLng: 'en',
  ns: ['topbar', 'settings', 'planUpgrade', 'store'],
  defaultNS: 'settings',
  interpolation: {
    escapeValue: false, // react already protects from xss
  },
});

export default i18n; 