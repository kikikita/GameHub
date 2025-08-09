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
      imageFormat: 'Image format',
      vertical: 'Vertical',
      horizontal: 'Horizontal',
      free: 'Free',
      pro: 'PRO⚡',
      upgrade: 'Upgrade',
    },
    planUpgrade: {
      infiniteEnergy: 'Infinite energy',
      wishesForShopping_one: '{{count}} wish for bringing your ideas to life',
      wishesForShopping_other: '{{count}} wishes for bringing your ideas to life',
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
      purchaseSuccess: 'Purchase successful!',
    },
    createNewStoryCard: {
      createStory: 'Create a Story',
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
      imageFormat: 'Формат изображений',
      vertical: 'Вертикальный',
      horizontal: 'Горизонтальный',
      free: 'Бесплатный',
      pro: 'PRO⚡',
      upgrade: 'Улучшить',
    },
    planUpgrade: {
      infiniteEnergy: 'Бесконечная энергия',
      wishesForShopping_one: '{{count}} желание для реализации своих идей',
      wishesForShopping_few: '{{count}} желания для реализации своих идей',
      wishesForShopping_many: '{{count}} желаний для реализации своих идей',
      wishesForShopping_other: '{{count}} желаний для реализации своих идей',
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
      purchaseSuccess: 'Желания успешно куплены!',
    },
    createNewStoryCard: {
      createStory: 'Создать историю',
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

// Persist language to localStorage on change so app restarts with correct language
i18n.on('languageChanged', (lng) => {
  try {
    localStorage.setItem('language', lng);
  } catch {
    // ignore storage errors (e.g., private mode)
  }
});

export default i18n; 