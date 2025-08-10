import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChevronRight } from "lucide-react";
import { useTranslation } from "react-i18next";

const languages: Record<string, string> = {
  en: "English",
  ru: "Русский",
};

type LanguageSelectorProps = {
  value: string;
  onChange: (code: string) => void;
};

export function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  const { t } = useTranslation("settings");
  return (
    <Select
      value={value}
      onValueChange={onChange}
    >
      <SelectTrigger className="w-full flex items-center justify-between px-4 py-3 text-foreground text-sm focus:outline-none rounded-2xl bg-transparent border-none hover:bg-muted/10 [&>svg]:hidden cursor-pointer">
        <span>{t("language")}</span>
        <span className="flex items-center gap-1 text-muted-foreground">
          <SelectValue placeholder={languages[value]} />
          <ChevronRight className="w-4 h-4" />
        </span>
      </SelectTrigger>
      <SelectContent>
        {Object.entries(languages).map(([code, label]) => (
          <SelectItem key={code} value={code} className="cursor-pointer">
            {label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
