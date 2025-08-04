import { useUser } from "@/api/user";
import i18n from "@/i18n";
import { useEffect } from "react";

export function useSyncLanguageToApp() {
  const { data: { language } } = useUser();

  useEffect(() => {
    i18n.changeLanguage(language);
  }, [language]);
}