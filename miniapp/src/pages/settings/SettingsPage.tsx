import { useSubscriptionPlan } from "@/api/plans";
import { useUpdateUser, useUser } from "@/api/user";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { navigationStore } from "@/stores/NavigationStore";
import { ChevronRight } from "lucide-react";
import { useTranslation } from "react-i18next";

export type Plan = "free" | "pro";

const languages: Record<string, string> = {
  en: "English",
  ru: "Русский",
};

export function SettingsPage() {
  const { t } = useTranslation('settings');
  const { data: { plan } } = useSubscriptionPlan();
  const { data: { language } } = useUser();
  const { mutate: updateUser } = useUpdateUser();

  return (
    <div className="p-4 space-y-6">
      <section className="bg-background/60 backdrop-blur-sm border border-border rounded-2xl p-4 space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground">{t("yourPlan")}</h3>
        <div className="text-4xl font-bold text-foreground capitalize">{t(plan)}</div>
        {plan === "free" && (
          <Button
            className="w-full"
            onClick={() => {
              navigationStore.setScreen("plan");
            }}
          >
            {t("upgrade")}
          </Button>
        )}
      </section>

      <section className="bg-background/60 backdrop-blur-sm border border-border rounded-2xl">
        <Select
          value={language}
          onValueChange={(code) => {
            updateUser({ language: code });
          }}
        >
          <SelectTrigger className="w-full flex items-center justify-between px-4 py-3 text-foreground text-sm focus:outline-none rounded-2xl bg-transparent border-none hover:bg-muted/10 [&>svg]:hidden cursor-pointer">
            <span>{t("language")}</span>
            <span className="flex items-center gap-1 text-muted-foreground">
              <SelectValue placeholder={languages[language]} />
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
      </section>
    </div>
  );
} 