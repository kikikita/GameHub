import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChevronRight } from "lucide-react";
import { useTranslation } from "react-i18next";

type ImageFormatSelectorProps = {
  value: string;
  onChange: (format: string) => void;
};

export function ImageFormatSelector({ value, onChange }: ImageFormatSelectorProps) {
  const { t } = useTranslation("settings");
  return (
    <Select
      value={value}
      onValueChange={onChange}
    >
      <SelectTrigger className="w-full flex items-center justify-between px-4 py-3 text-foreground text-sm focus:outline-none rounded-2xl bg-transparent border-none hover:bg-muted/10 [&>svg]:hidden cursor-pointer">
        <span>{t("imageFormat")}</span>
        <span className="flex items-center gap-1 text-muted-foreground">
          <SelectValue placeholder={t(value)} />
          <ChevronRight className="w-4 h-4" />
        </span>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="vertical" className="cursor-pointer">
          {t("vertical")}
        </SelectItem>
        <SelectItem value="horizontal" className="cursor-pointer">
          {t("horizontal")}
        </SelectItem>
      </SelectContent>
    </Select>
  );
}
